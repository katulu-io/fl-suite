/*
Copyright 2022.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package controllers

import (
	"context"
	"fmt"
	"strconv"
	"time"

	"github.com/katulu-io/fl-suite/fl-operator/pkg/resources"
	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	logger "sigs.k8s.io/controller-runtime/pkg/log"

	flv1alpha1 "github.com/katulu-io/fl-suite/fl-operator/api/v1alpha1"
	"github.com/katulu-io/fl-suite/fl-operator/pkg/utils"
)

// FlEdgeReconciler reconciles a FlEdge object
type FlEdgeReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

//+kubebuilder:rbac:groups=fl.katulu.io,resources=fledges,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=fl.katulu.io,resources=fledges/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=fl.katulu.io,resources=fledges/finalizers,verbs=update
//+kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch;delete

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
// TODO(user): Modify the Reconcile function to compare the state specified by
// the FlEdge object against the actual cluster state, and then
// perform operations to make the cluster state reflect the state specified by
// the user.
//
// For more details, check Reconcile and its Result here:
// - https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.12.1/pkg/reconcile
func (r *FlEdgeReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := logger.FromContext(ctx)
	flEdge := &flv1alpha1.FlEdge{}

	err := r.Get(ctx, req.NamespacedName, flEdge)
	if err != nil {
		if errors.IsNotFound(err) {
			log.Error(err, "FlEdge resource not found. Ignoring since object must be deleted")
			return ctrl.Result{}, nil
		}

		log.Error(err, "Could not get FlEdge")
		return ctrl.Result{}, err
	}

	if flEdge.Spec.Auth.Spire != nil {
		err = r.setupSpireAuthentication(ctx, flEdge)
		if err != nil {
			log.Error(err, "Could not setup the spire authentication")
			return ctrl.Result{}, err
		}
	}

	return ctrl.Result{
		RequeueAfter: time.Second * 5,
	}, nil
}

func (r *FlEdgeReconciler) setupSpireAuthentication(
	ctx context.Context,
	flEdge *flv1alpha1.FlEdge,
) error {
	log := logger.FromContext(ctx)

	namespacedName := types.NamespacedName{
		Name:      fmt.Sprintf("%s-spire-agent", flEdge.Name),
		Namespace: flEdge.Namespace,
	}
	configMapName, err := r.setupSpireAgentConfigMap(ctx, flEdge, namespacedName)
	if err != nil {
		log.Error(err, "Could not setup the spire-agent configmap")
		return err
	}

	err = r.setupSpireAgentDeployment(ctx, flEdge, namespacedName, configMapName)
	if err != nil {
		log.Error(err, "Could not setup the spire-agent pod")
		return err
	}

	flEdge.Status.CurrentConfigMapName = configMapName
	flEdge.Status.CurrentDeploymentName = namespacedName.Name
	err = r.Status().Update(ctx, flEdge)
	if err != nil {
		log.Error(err, "Could not update the fledge status")
		return err
	}

	return nil
}

func (r *FlEdgeReconciler) setupSpireAgentConfigMap(
	ctx context.Context,
	flEdge *flv1alpha1.FlEdge,
	configMapName types.NamespacedName,
) (string, error) {
	log := logger.FromContext(ctx)

	configMapContent, err := resources.RenderSpireAgentConfig(
		resources.SpireAgentConfigContext{
			ServerAddress:           flEdge.Spec.Auth.Spire.ServerAddress,
			ServerPort:              flEdge.Spec.Auth.Spire.ServerPort,
			TrustDomain:             flEdge.Spec.Auth.Spire.TrustDomain,
			JoinToken:               flEdge.Spec.Auth.Spire.JoinToken,
			SkipKubeletVerification: strconv.FormatBool(flEdge.Spec.Auth.Spire.SkipKubeletVerification),
		},
		"../deployment/spire-agent.conf.tpl",
	)
	if err != nil {
		log.Error(err, "Could not render spire-agent config")
		return "", err
	}

	configMap := &corev1.ConfigMap{
		TypeMeta: metav1.TypeMeta{
			Kind:       "ConfigMap",
			APIVersion: "v1",
		},
		ObjectMeta: metav1.ObjectMeta{
			Name:      configMapName.Name,
			Namespace: configMapName.Namespace,
		},
		Data: map[string]string{
			"agent.conf": configMapContent,
		},
	}
	hash, _ := utils.HashConfigMap(configMap)
	if err != nil {
		log.Error(err, "Could not hash the spire-agent configmap name")
		return "", err
	}
	configMap.ObjectMeta.Name = fmt.Sprintf("%s-%s", configMapName.Name, hash)

	err = ctrl.SetControllerReference(flEdge, configMap, r.Scheme)
	if err != nil {
		log.Error(err, "Could not set controller reference in the spire-agent configmap")
		return "", err
	}

	err = r.Patch(ctx, configMap, client.Apply, client.ForceOwnership, client.FieldOwner(flEdge.GetName()))
	if err != nil {
		log.Error(err, "Could not apply the spire-agent configmap")
		return "", err
	}

	return configMap.ObjectMeta.Name, nil
}

func (r *FlEdgeReconciler) setupSpireAgentDeployment(
	ctx context.Context,
	flEdge *flv1alpha1.FlEdge,
	namespaceName types.NamespacedName,
	configMapName string,
) error {
	log := logger.FromContext(ctx)

	configMapVolumeName := "spire-agent-config"
	labels := map[string]string{
		"app": "spire-agent",
	}
	// join-tokens cannot be reused to authenticate multiple spire-agent hence the number of replicas set 1.
	replicas := int32(1)
	hostPathType := corev1.HostPathDirectoryOrCreate
	deployment := &appsv1.Deployment{
		TypeMeta: metav1.TypeMeta{
			Kind:       "Deployment",
			APIVersion: "apps/v1",
		},
		ObjectMeta: metav1.ObjectMeta{
			Name:      namespaceName.Name,
			Namespace: namespaceName.Namespace,
			Labels:    labels,
		},
		Spec: appsv1.DeploymentSpec{
			Replicas: &replicas,
			Selector: &metav1.LabelSelector{
				MatchLabels: labels,
			},
			Template: corev1.PodTemplateSpec{
				ObjectMeta: metav1.ObjectMeta{
					Labels: labels,
				},
				Spec: corev1.PodSpec{
					DNSPolicy: corev1.DNSClusterFirstWithHostNet,
					Containers: []corev1.Container{
						{
							Name:            "spire-agent",
							Image:           "gcr.io/spiffe-io/spire-agent:1.3.0",
							ImagePullPolicy: corev1.PullIfNotPresent,
							Args:            []string{"-config", "/run/spire/config/agent.conf"},
							VolumeMounts: []corev1.VolumeMount{
								{
									Name:      configMapVolumeName,
									MountPath: "/run/spire/config",
									ReadOnly:  true,
								},
								{
									Name:      "spire-agent-socket",
									MountPath: "/run/spire/sockets",
									ReadOnly:  false,
								},
							},
							LivenessProbe: &corev1.Probe{
								ProbeHandler: corev1.ProbeHandler{
									Exec: &corev1.ExecAction{
										Command: []string{"/opt/spire/bin/spire-agent", "healthcheck", "-socketPath", "/run/spire/sockets/agent.sock"},
									},
								},
								FailureThreshold:    2,
								InitialDelaySeconds: 15,
								PeriodSeconds:       60,
								TimeoutSeconds:      3,
							},
							ReadinessProbe: &corev1.Probe{
								ProbeHandler: corev1.ProbeHandler{
									Exec: &corev1.ExecAction{
										Command: []string{"/opt/spire/bin/spire-agent", "healthcheck", "-socketPath", "/run/spire/sockets/agent.sock", "--shallow"},
									},
								},
								InitialDelaySeconds: 5,
								PeriodSeconds:       5,
							},
						},
					},
					Volumes: []corev1.Volume{
						{
							Name: configMapVolumeName,
							VolumeSource: corev1.VolumeSource{
								ConfigMap: &corev1.ConfigMapVolumeSource{
									LocalObjectReference: corev1.LocalObjectReference{
										Name: configMapName,
									},
								},
							},
						},
						{
							Name: "spire-agent-socket",
							VolumeSource: corev1.VolumeSource{
								HostPath: &corev1.HostPathVolumeSource{
									Path: "/run/spire/sockets",
									Type: &hostPathType,
								},
							},
						},
					},
				},
			},
		},
	}

	err := ctrl.SetControllerReference(flEdge, deployment, r.Scheme)
	if err != nil {
		log.Error(err, "Could not set controller reference in the spire-agent deployment")
		return err
	}

	err = r.Patch(ctx, deployment, client.Apply, client.ForceOwnership, client.FieldOwner(flEdge.GetName()))
	if err != nil {
		log.Error(err, "Could not apply spire-agent deployment")
		return err
	}

	return nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *FlEdgeReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&flv1alpha1.FlEdge{}).
		Owns(&appsv1.Deployment{}).
		Owns(&appsv1.Deployment{}).
		Complete(r)
}
