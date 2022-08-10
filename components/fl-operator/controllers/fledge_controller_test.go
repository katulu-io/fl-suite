package controllers

import (
	"time"

	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"

	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	rbacv1 "k8s.io/api/rbac/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"

	"github.com/katulu-io/fl-suite/fl-operator/api/v1alpha1"
)

var _ = Describe("FlEdge Controller", func() {
	const (
		timeout  = time.Second * 10
		interval = time.Millisecond * 250
	)
	var flEdgeKey types.NamespacedName
	var flEdge *v1alpha1.FlEdge
	var ownerReference metav1.OwnerReference

	BeforeEach(func() {
		flEdgeKey = types.NamespacedName{
			Name: "sample",
		}
		flEdge = &v1alpha1.FlEdge{
			TypeMeta: metav1.TypeMeta{
				APIVersion: "fl.katulu.io/v1alpha1",
				Kind:       "FlEdge",
			},
			ObjectMeta: metav1.ObjectMeta{
				Name: flEdgeKey.Name,
			},
			Spec: v1alpha1.FlEdgeSpec{
				Auth: v1alpha1.FlEdgeAuth{
					Spire: &v1alpha1.FlEdgeSpireAuth{
						ServerAddress:           "test-server",
						ServerPort:              8888,
						TrustDomain:             "example.com",
						JoinToken:               "test-join-token-goes-here",
						SkipKubeletVerification: true,
					},
				},
			},
		}
		Expect(k8sClient.Create(ctx, flEdge)).Should(Succeed())

		// Eventually the status is set
		Eventually(func(g Gomega) {
			err := k8sClient.Get(ctx, flEdgeKey, flEdge)
			g.Expect(err).NotTo(HaveOccurred())

			g.Expect(flEdge.Status.CurrentConfigMapName).NotTo(Equal(""))
		}, timeout, interval).Should(Succeed())

		blockOwnerDeletion := true
		ownerReference = metav1.OwnerReference{
			APIVersion:         "fl.katulu.io/v1alpha1",
			Kind:               "FlEdge",
			UID:                flEdge.UID,
			Name:               flEdge.Name,
			Controller:         &blockOwnerDeletion,
			BlockOwnerDeletion: &blockOwnerDeletion,
		}
	})

	AfterEach(func() {
		Expect(k8sClient.Delete(ctx, flEdge)).Should(Succeed())
	})

	Context("When creating a new fl-edge", func() {
		It("should bootstrap a clusterrolebinding, deployment and a configmap", func() {
			// We check that the owner reference is set on each resource to assert that the resource will be deleted because
			// envtest does not run the gc controller in charge of deleting the resources.
			// ref: https://book-v2.book.kubebuilder.io/reference/envtest.html#testing-considerations

			// Eventually a new namespace is created
			Eventually(func(g Gomega) {
				key := types.NamespacedName{
					Name: "sample-spire-agent",
				}
				c := &corev1.Namespace{}
				err := k8sClient.Get(ctx, key, c)

				g.Expect(err).NotTo(HaveOccurred())
				g.Expect(c.OwnerReferences).To(ContainElement(ownerReference))
			}, timeout, interval).Should(Succeed())

			// Eventually the clusterrolebinding is created
			Eventually(func(g Gomega) {
				key := types.NamespacedName{
					Name: "sample-spire-agent",
				}
				c := &rbacv1.ClusterRoleBinding{}
				err := k8sClient.Get(ctx, key, c)

				g.Expect(err).NotTo(HaveOccurred())
				g.Expect(c.OwnerReferences).To(ContainElement(ownerReference))
			}, timeout, interval).Should(Succeed())

			// Eventually the service-account is created
			Eventually(func(g Gomega) {
				key := types.NamespacedName{
					Name:      "sample-spire-agent",
					Namespace: "sample-spire-agent",
				}
				c := &corev1.ServiceAccount{}
				err := k8sClient.Get(ctx, key, c)

				g.Expect(err).NotTo(HaveOccurred())
				g.Expect(c.OwnerReferences).To(ContainElement(ownerReference))
			}, timeout, interval).Should(Succeed())

			// Eventually the configmap is created
			Eventually(func(g Gomega) {
				key := types.NamespacedName{
					Name:      flEdge.Status.CurrentConfigMapName,
					Namespace: "sample-spire-agent",
				}
				c := &corev1.ConfigMap{}
				err := k8sClient.Get(ctx, key, c)

				g.Expect(err).NotTo(HaveOccurred())
				g.Expect(c.OwnerReferences).To(ContainElement(ownerReference))
			}, timeout, interval).Should(Succeed())

			// Eventually the deployment is created
			Eventually(func(g Gomega) {
				key := types.NamespacedName{
					Name:      "sample-spire-agent",
					Namespace: "sample-spire-agent",
				}
				d := &appsv1.Deployment{}
				err := k8sClient.Get(ctx, key, d)

				g.Expect(err).NotTo(HaveOccurred())
				g.Expect(d.OwnerReferences).To(ContainElement(ownerReference))
				g.Expect(isDeploymentUsingConfigMap(d, flEdge.Status.CurrentConfigMapName)).To(BeTrue())
				g.Expect(d.Spec.Template.Spec.ServiceAccountName).To(Equal("sample-spire-agent"))
			}, timeout, interval).Should(Succeed())
		})
	})

	Context("When updating a fl-edge", func() {
		It("should create a new configmap and update the deployment", func() {
			flEdge.Spec.Auth.Spire.ServerAddress = "spire-server"
			flEdge.Spec.Auth.Spire.ServerPort = 8000
			flEdge.Spec.Auth.Spire.TrustDomain = "another-domain.com"
			Expect(k8sClient.Update(ctx, flEdge)).Should(Succeed())

			// Eventually the FlEdge status is updated with a new configmap name
			updatedFlEdge := &v1alpha1.FlEdge{}
			Eventually(func(g Gomega) {
				err := k8sClient.Get(ctx, flEdgeKey, updatedFlEdge)
				g.Expect(err).NotTo(HaveOccurred())
				g.Expect(flEdge.Status.CurrentConfigMapName).NotTo(Equal(updatedFlEdge.Status.CurrentConfigMapName))
			}).Should(Succeed())

			// Eventually a new configmap is created
			Eventually(func(g Gomega) {
				key := types.NamespacedName{
					Name:      updatedFlEdge.Status.CurrentConfigMapName,
					Namespace: "sample-spire-agent",
				}
				c := &corev1.ConfigMap{}
				err := k8sClient.Get(ctx, key, c)
				g.Expect(err).NotTo(HaveOccurred())
			}, timeout, interval).Should(Succeed())

			// Eventually the deployment is updated
			Eventually(func(g Gomega) {
				key := types.NamespacedName{
					Name:      "sample-spire-agent",
					Namespace: "sample-spire-agent",
				}
				d := &appsv1.Deployment{}
				err := k8sClient.Get(ctx, key, d)

				g.Expect(err).NotTo(HaveOccurred())
				g.Expect(isDeploymentUsingConfigMap(d, updatedFlEdge.Status.CurrentConfigMapName)).To(BeTrue())
			}, timeout, interval).Should(Succeed())
		})
	})
})

func isDeploymentUsingConfigMap(d *appsv1.Deployment, configMapName string) bool {
	for v := range d.Spec.Template.Spec.Volumes {
		configMap := d.Spec.Template.Spec.Volumes[v].VolumeSource.ConfigMap
		if configMap.Name == configMapName {
			return true
		}
	}
	return false
}
