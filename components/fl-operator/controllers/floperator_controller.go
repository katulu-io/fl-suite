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
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	logger "sigs.k8s.io/controller-runtime/pkg/log"

	flv1alpha1 "github.com/katulu-io/fl-suite/fl-operator/api/v1alpha1"
	orchestratorClient "github.com/katulu-io/fl-suite/fl-operator/pkg/client"
	"github.com/katulu-io/fl-suite/fl-operator/pkg/resources"
	pb "github.com/katulu-io/fl-suite/fl-orchestrator/pkg/proto"
)

// FlOperatorReconciler reconciles a FlOperator object
type FlOperatorReconciler struct {
	client.Client
	Scheme               *runtime.Scheme
	EnvoyproxyConfigFile string
	OrchestratorClient   *orchestratorClient.Client
}

const (
	configMapNameEnvoyProxy  = "fl-operator-envoyproxy"
	deploymentNameEnvoyProxy = "fl-operator-envoyproxy"
	serviceNameEnvoyProxy    = "fl-operator-envoyproxy"
	podNameFlClient          = "flower-client"
)

//+kubebuilder:rbac:groups=fl.katulu.io,resources=floperators,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=fl.katulu.io,resources=floperators/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=fl.katulu.io,resources=floperators/finalizers,verbs=update
//+kubebuilder:rbac:groups="",resources=configmaps,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups="",resources=services,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups="",resources=pods,verbs=get;list;watch;create;update;patch;delete

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
// TODO(user): Modify the Reconcile function to compare the state specified by
// the FlOperator object against the actual cluster state, and then
// perform operations to make the cluster state reflect the state specified by
// the user.
//
// For more details, check Reconcile and its Result here:
// - https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.11.0/pkg/reconcile
func (r *FlOperatorReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := logger.FromContext(ctx)
	flOperator := &flv1alpha1.FlOperator{}

	err := r.Get(ctx, req.NamespacedName, flOperator)
	if err != nil {
		if errors.IsNotFound(err) {
			log.Info("FlOperator resource not found. Ignoring since object must be deleted")
			return ctrl.Result{}, nil
		}

		log.Error(err, "Could not get FlOperator")
		return ctrl.Result{}, err
	}

	// Bootstrap envoy configmap, deployment and service
	// These resources should always be there for the tasks
	// coming via gRPC from FL-Orchestrator
	err = r.bootstrapEnvoyConfigMap(ctx, req.NamespacedName.Namespace, flOperator)
	if err != nil {
		log.Error(err, "Could not create envoyproxy configmap")
		return ctrl.Result{}, err
	}

	err = r.bootstrapEnvoyDeployment(ctx, req.NamespacedName.Namespace, flOperator)
	if err != nil {
		log.Error(err, "Could not create envoyproxy deployment")
		return ctrl.Result{}, err
	}

	err = r.bootstrapEnvoyService(ctx, req.NamespacedName.Namespace, flOperator)
	if err != nil {
		log.Error(err, "Could not create envoyproxy service")
		return ctrl.Result{}, err
	}

	// Create gRPC client for connection to FL-Orchestrator
	if r.OrchestratorClient == nil {
		log.Info("Creating OrchestratorClient")

		timeout := time.Second * 30 // TODO move this into the spec?
		serverAddress := fmt.Sprintf("%s.%s:9080", serviceNameEnvoyProxy, req.Namespace)
		dialOptions := []grpc.DialOption{
			grpc.WithTransportCredentials(insecure.NewCredentials()),
		}
		conn, err := grpc.Dial(serverAddress, dialOptions...)
		if err != nil {
			log.Error(err, "Could not create gRPC connection")
			return ctrl.Result{}, err
		}

		cl := orchestratorClient.NewClient(conn, timeout)
		r.OrchestratorClient = &cl
	}

	// Fetch tasks from FL-Orchestrator
	response, err := r.OrchestratorClient.GetTasks(ctx)
	if err != nil {
		log.Error(err, "Could not fetch tasks")
		return ctrl.Result{
			Requeue: true,
		}, err
	}

	tasks := response.GetTasks()
	log.Info(fmt.Sprintf("Got %d tasks from FL-Orchestrator", len(tasks)))

	// First get the list of all running fl-client pods
	podsList := &corev1.PodList{}
	opts := []client.ListOption{
		client.InNamespace(req.NamespacedName.Namespace),
		client.MatchingLabels{resources.FlClientDeploymentLabelKey: resources.FlClientDeploymentLabelValue},
	}
	err = r.List(ctx, podsList, opts...)
	if err != nil {
		log.Error(err, "Could not get the list of fl-client deployments")
		return ctrl.Result{
			Requeue: true,
		}, err
	}

	for _, task := range tasks {
		log.Info(fmt.Sprintf("Found run ID: %s", task.ID))

		podName := types.NamespacedName{
			Name:      getPodName(task),
			Namespace: req.Namespace,
		}

		found, err := r.isResourceFound(ctx, podName, &corev1.Pod{})
		if err != nil {
			log.Error(err, "Failed to find out if fl-client is running")
			continue
		}
		if found {
			log.Info("Pod is already running")
			continue
		}

		log.Info("Pod not found, creating...")
		envoyConfigContext := resources.EnvoyConfigContext{
			EndpointAddress: flOperator.Spec.FlOrchestratorURL,
			EndpointPort:    flOperator.Spec.FlOrchestratorPort,
			EndpointSNI:     task.SNI,
			SourceName:      "flower-client",
			DestinationName: task.Workflow,
		}
		configMapName := types.NamespacedName{
			Name:      task.Workflow,
			Namespace: req.Namespace,
		}
		err = r.setupEnvoyproxyConfig(ctx, flOperator, configMapName, envoyConfigContext)
		if err != nil {
			log.Error(err, "Failed to setup flower-client's envoy config")
			continue
		}

		pod := resources.NewPod(task, podName, task.Workflow)

		err = ctrl.SetControllerReference(flOperator, pod, r.Scheme)
		if err != nil {
			log.Error(err, "Failed to set controller reference for the pod")
			continue
		}

		err = r.Create(ctx, pod)
		if err != nil {
			log.Error(err, "Failed to create pod")
			continue
		}
	}

	return ctrl.Result{
		RequeueAfter: time.Second * 5,
	}, nil
}

func (r *FlOperatorReconciler) bootstrapEnvoyConfigMap(ctx context.Context, namespace string, flOperator *flv1alpha1.FlOperator) error {
	// Setup envoy proxy config map
	envoyConfigContext := resources.EnvoyConfigContext{
		EndpointAddress: flOperator.Spec.FlOrchestratorURL,
		EndpointPort:    flOperator.Spec.FlOrchestratorPort,
		EndpointSNI:     flOperator.Spec.FlOrchestratorSNI,
		SourceName:      "fl-operator",
		DestinationName: "fl-orchestrator",
	}
	configMapName := types.NamespacedName{
		Name:      configMapNameEnvoyProxy,
		Namespace: namespace,
	}
	return r.setupEnvoyproxyConfig(ctx, flOperator, configMapName, envoyConfigContext)
}

func (r *FlOperatorReconciler) bootstrapEnvoyDeployment(ctx context.Context, namespace string, flOperator *flv1alpha1.FlOperator) error {
	// Setup envoyproxy deployment
	deploymentName := types.NamespacedName{
		Name:      deploymentNameEnvoyProxy,
		Namespace: namespace,
	}
	found, err := r.isResourceFound(ctx, deploymentName, &appsv1.Deployment{})
	if err != nil {
		return err
	}
	if found {
		return nil
	}

	dep := resources.NewEnvoyproxyDeployment(deploymentName)
	err = ctrl.SetControllerReference(flOperator, dep, r.Scheme)
	if err != nil {
		return err
	}
	return r.Create(ctx, dep)
}

func (r *FlOperatorReconciler) bootstrapEnvoyService(ctx context.Context, namespace string, flOperator *flv1alpha1.FlOperator) error {
	// Setup envoyproxy service
	serviceName := types.NamespacedName{
		Name:      serviceNameEnvoyProxy,
		Namespace: namespace,
	}
	found, err := r.isResourceFound(ctx, serviceName, &corev1.Service{})
	if err != nil {
		return err
	}
	if found {
		return nil
	}

	svc := resources.NewEnvoyproxyService(serviceName)
	err = ctrl.SetControllerReference(flOperator, svc, r.Scheme)
	if err != nil {
		return err
	}
	return r.Create(ctx, svc)
}

func (r *FlOperatorReconciler) setupEnvoyproxyConfig(
	ctx context.Context,
	flOperator *flv1alpha1.FlOperator,
	configMapName types.NamespacedName,
	envoyConfigContext resources.EnvoyConfigContext,
) error {
	found, err := r.isResourceFound(ctx, configMapName, &corev1.ConfigMap{})
	if err != nil {
		return err
	}
	if found {
		return nil
	}

	envoyConfigContent, err := resources.RenderEnvoyproxyConfig(envoyConfigContext, r.EnvoyproxyConfigFile)
	if err != nil {
		return err
	}

	cm := resources.NewConfigMap(configMapName, envoyConfigContent)
	err = ctrl.SetControllerReference(flOperator, cm, r.Scheme)
	if err != nil {
		return err
	}
	err = r.Create(ctx, cm)
	if err != nil {
		return err
	}

	return nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *FlOperatorReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&flv1alpha1.FlOperator{}).
		Complete(r)
}

// Find out if a certain resource is running
func (r *FlOperatorReconciler) isResourceFound(ctx context.Context, namespacedName types.NamespacedName, object client.Object) (bool, error) {
	err := r.Get(ctx, namespacedName, object)
	if err != nil {
		if errors.IsNotFound(err) {
			return false, nil
		}
		return false, err
	}

	return true, nil
}

func getPodName(task *pb.OrchestratorMessage_TaskSpec) string {
	return fmt.Sprintf("%s-%s", podNameFlClient, task.Workflow)
}
