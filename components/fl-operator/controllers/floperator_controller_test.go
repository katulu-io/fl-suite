package controllers

import (
	"time"

	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"

	"github.com/katulu-io/fl-suite/fl-operator/api/v1alpha1"
)

var _ = Describe("FlOperator Controller", func() {
	const (
		flOperatorName      = "test-fl-operator"
		flOperatorNamespace = "default"

		timeout  = time.Second * 10
		interval = time.Millisecond * 250
	)

	var flOperator *v1alpha1.FlOperator

	AfterEach(func() {
		Expect(k8sClient.Delete(ctx, flOperator)).Should(Succeed())
	})

	Context("When creating a new fl-operator", func() {
		It("should bootstrap the envoy proxy with configmap, deployment and service resources", func() {
			flOperator = &v1alpha1.FlOperator{
				TypeMeta: metav1.TypeMeta{
					APIVersion: "fl.katulu.io/v1alpha1",
					Kind:       "FlOperator",
				},
				ObjectMeta: metav1.ObjectMeta{
					Name:      flOperatorName,
					Namespace: flOperatorNamespace,
				},
				Spec: v1alpha1.FlOperatorSpec{
					FlOrchestratorURL: "orchestrator-url",
					FlOrchestratorSNI: "orchestrator-sni",
				},
			}
			Expect(k8sClient.Create(ctx, flOperator)).Should(Succeed())

			// Eventually the flOperator resource is created
			flOperatorLookupKey := types.NamespacedName{
				Name:      flOperatorName,
				Namespace: flOperatorNamespace,
			}
			Eventually(func() bool {
				err := k8sClient.Get(ctx, flOperatorLookupKey, &v1alpha1.FlOperator{})
				return err == nil
			}, timeout, interval).Should(BeTrue())

			// Eventually envoy configmap resource is created
			envoyConfigmapLookupKey := types.NamespacedName{
				Name:      configMapNameEnvoyProxy,
				Namespace: flOperatorNamespace,
			}
			Eventually(func() bool {
				err := k8sClient.Get(ctx, envoyConfigmapLookupKey, &corev1.ConfigMap{})
				return err == nil
			}, timeout, interval).Should(BeTrue())

			// Eventually envoy deployment resource is created
			envoyDeploymentLookupKey := types.NamespacedName{
				Name:      deploymentNameEnvoyProxy,
				Namespace: flOperatorNamespace,
			}
			Eventually(func() bool {
				err := k8sClient.Get(ctx, envoyDeploymentLookupKey, &appsv1.Deployment{})
				return err == nil
			}, timeout, interval).Should(BeTrue())

			// Eventually envoy service resource is created
			envoyServiceLookupKey := types.NamespacedName{
				Name:      serviceNameEnvoyProxy,
				Namespace: flOperatorNamespace,
			}
			Eventually(func() bool {
				err := k8sClient.Get(ctx, envoyServiceLookupKey, &corev1.Service{})
				return err == nil
			}, timeout, interval).Should(BeTrue())
		})
	})
})
