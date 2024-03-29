package resources

import (
	"bytes"
	"html/template"
	"os"

	flv1alpha1 "github.com/katulu-io/fl-suite/fl-operator/api/v1alpha1"
	pb "github.com/katulu-io/fl-suite/fl-orchestrator/pkg/api/fl_orchestrator/v1"
	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"

	"github.com/katulu-io/fl-suite/fl-operator/pkg/utils"
)

const (
	envoyConfigFilename = "envoy.yaml"

	FlClientDeploymentLabelKey   = "app"
	FlClientDeploymentLabelValue = "flower-client"
)

type EnvoyConfigContext struct {
	EndpointAddress string
	EndpointPort    int16
	EndpointSNI     string
	SourceName      string
	DestinationName string
}

func RenderEnvoyproxyConfig(context EnvoyConfigContext, envoyConfigFile string) (string, error) {
	envoyConfigTemplate, err := os.ReadFile(envoyConfigFile)
	if err != nil {
		return "", err
	}

	t, err := template.New("envoy-config").Parse(string(envoyConfigTemplate))
	if err != nil {
		return "", err
	}

	out := &bytes.Buffer{}

	err = t.Execute(out, context)
	if err != nil {
		return "", err
	}

	return out.String(), nil
}

func RenderSpireAgentConfig(context SpireAgentConfigContext, envoyConfigFile string) (string, error) {
	envoyConfigTemplate, err := os.ReadFile(envoyConfigFile)
	if err != nil {
		return "", err
	}

	t, err := template.New("spire-agent").Parse(string(envoyConfigTemplate))
	if err != nil {
		return "", err
	}

	out := &bytes.Buffer{}

	err = t.Execute(out, context)
	if err != nil {
		return "", err
	}

	return out.String(), nil
}

type SpireAgentConfigContext struct {
	ServerAddress           string
	ServerPort              int16
	TrustDomain             string
	SkipKubeletVerification string
	JoinToken               string
}

// Creates new pod for the flower-client
func NewPod(
	task *pb.OrchestratorMessage_TaskSpec,
	name types.NamespacedName,
	envoyConfigName string,
	registryCredentials *flv1alpha1.FlOperatorRegistryCredentials,
) *corev1.Pod {
	shareProcessNamespace := true
	labels := map[string]string{
		FlClientDeploymentLabelKey: FlClientDeploymentLabelValue,
		"run-id":                   string(task.ID),
		"spire-workload":           "flower-client",
	}
	envoyConfigVolumeKey := "envoy-config"

	pod := &corev1.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name:      name.Name,
			Namespace: name.Namespace,
			Labels:    labels,
		},
		Spec: corev1.PodSpec{
			// For the flower-client to pkill the envoyproxy as below instructed, the containers need to share the same
			// process namespace.
			ShareProcessNamespace: &shareProcessNamespace,
			Containers: []corev1.Container{
				{
					Name:            "flower-client",
					Image:           task.Executor.GetOciExecutor().Image,
					ImagePullPolicy: corev1.PullIfNotPresent,
					Command:         []string{"/bin/bash", "-c"},
					// Assuming all flower-clients run with: python /app/main.py
					// "pkill envoy" is needed to kill the envoyproxy once the flower-client finishes the fl-run and the
					// the pod is marked as completed.
					Args: []string{"python /app/main.py && pkill envoy"},
				},
				{
					Name:            "envoyproxy",
					Image:           "envoyproxy/envoy:v1.20-latest",
					ImagePullPolicy: corev1.PullIfNotPresent,
					Args:            []string{"-l", "debug", "--local-address-ip-version", "v4", "-c", "/run/envoy/envoy.yaml", "--base-id", "1"},
					Ports: []corev1.ContainerPort{
						{
							ContainerPort: 9080,
						},
					},
					VolumeMounts: []corev1.VolumeMount{
						{
							Name:      envoyConfigVolumeKey,
							MountPath: "/run/envoy",
							ReadOnly:  true,
						},
						{
							Name:      "spire-agent-socket",
							MountPath: "/run/spire/sockets",
							ReadOnly:  true,
						},
					},
					Env: []corev1.EnvVar{
						{
							Name: "ENVOY_UID",
						},
					},
				},
			},
			// RestartPolicy: OnFailure is preferred because it allows the pod to fail on transitive errors
			// (e.g flower-client's envoyproxy not ready which causes it to crash)
			RestartPolicy: "OnFailure",
			Volumes: []corev1.Volume{
				{
					Name: envoyConfigVolumeKey,
					VolumeSource: corev1.VolumeSource{
						ConfigMap: &corev1.ConfigMapVolumeSource{
							LocalObjectReference: corev1.LocalObjectReference{
								Name: envoyConfigName,
							},
						},
					},
				},
				{
					Name: "spire-agent-socket",
					VolumeSource: corev1.VolumeSource{
						HostPath: &corev1.HostPathVolumeSource{
							Path: "/run/spire/sockets",
							Type: utils.HostPathTypePtr(corev1.HostPathDirectoryOrCreate),
						},
					},
				},
			},
		},
	}

	if registryCredentials != nil {
		pod.Spec.ImagePullSecrets = []corev1.LocalObjectReference{{Name: registryCredentials.Secret}}
	}

	return pod
}

// Creates a new envoy proxy deployment
func NewEnvoyproxyDeployment(name types.NamespacedName) *appsv1.Deployment {
	labels := map[string]string{
		"app":            name.Name,
		"spire-workload": "fl-operator",
	}

	const envoyConfigVolumeKey = "envoy-config"

	return &appsv1.Deployment{
		ObjectMeta: metav1.ObjectMeta{
			Name:      name.Name,
			Namespace: name.Namespace,
			Labels:    labels,
		},
		Spec: appsv1.DeploymentSpec{
			Replicas: utils.Int32Ptr(1),
			Selector: &metav1.LabelSelector{
				MatchLabels: labels,
			},
			Template: corev1.PodTemplateSpec{
				ObjectMeta: metav1.ObjectMeta{
					Labels: labels,
				},
				Spec: corev1.PodSpec{
					Containers: []corev1.Container{
						{
							Name:            "envoyproxy",
							Image:           "envoyproxy/envoy:v1.20-latest",
							ImagePullPolicy: corev1.PullIfNotPresent,
							Args:            []string{"-l", "debug", "--local-address-ip-version", "v4", "-c", "/run/envoy/envoy.yaml", "--base-id", "1"},
							Ports: []corev1.ContainerPort{
								{
									ContainerPort: 9080,
								},
							},
							VolumeMounts: []corev1.VolumeMount{
								{
									Name:      envoyConfigVolumeKey,
									MountPath: "/run/envoy",
									ReadOnly:  true,
								},
								{
									Name:      "spire-agent-socket",
									MountPath: "/run/spire/sockets",
									ReadOnly:  true,
								},
							},
							Env: []corev1.EnvVar{
								{
									Name: "ENVOY_UID",
								},
							},
						},
					},
					Volumes: []corev1.Volume{
						{
							Name: envoyConfigVolumeKey,
							VolumeSource: corev1.VolumeSource{
								ConfigMap: &corev1.ConfigMapVolumeSource{
									LocalObjectReference: corev1.LocalObjectReference{
										Name: name.Name,
									},
								},
							},
						},
						{
							Name: "spire-agent-socket",
							VolumeSource: corev1.VolumeSource{
								HostPath: &corev1.HostPathVolumeSource{
									Path: "/run/spire/sockets",
									Type: utils.HostPathTypePtr(corev1.HostPathDirectoryOrCreate),
								},
							},
						},
					},
				},
			},
		},
	}
}

func NewEnvoyproxyService(name types.NamespacedName) *corev1.Service {
	return &corev1.Service{
		ObjectMeta: metav1.ObjectMeta{
			Name:      name.Name,
			Namespace: name.Namespace,
		},
		Spec: corev1.ServiceSpec{
			Ports: []corev1.ServicePort{
				{
					Name:     "grpc",
					Port:     9080,
					Protocol: "TCP",
				},
			},
			Selector: map[string]string{
				"app": name.Name,
			},
		},
	}
}

func NewConfigMap(name types.NamespacedName, envoyConfigContent string) *corev1.ConfigMap {
	return &corev1.ConfigMap{
		ObjectMeta: metav1.ObjectMeta{
			Name:      name.Name,
			Namespace: name.Namespace,
		},
		Data: map[string]string{
			envoyConfigFilename: envoyConfigContent,
		},
	}
}
