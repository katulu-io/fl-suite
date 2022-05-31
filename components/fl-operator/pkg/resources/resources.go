package resources

import (
	"bytes"
	"html/template"
	"io/ioutil"

	pb "github.com/katulu-io/fl-suite/fl-orchestrator/pkg/proto"
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
	envoyConfigTemplate, err := ioutil.ReadFile(envoyConfigFile)
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

// Creates a new flower-client deployment that contains the envoy-proxy plus the fl-client itself
func NewDeployment(task *pb.OrchestratorMessage_TaskSpec, name types.NamespacedName, envoyConfigName string) *appsv1.Deployment {
	labels := map[string]string{
		FlClientDeploymentLabelKey: FlClientDeploymentLabelValue,
		"run-id":                   string(task.ID),
	}

	envoyConfigVolumeKey := "envoy-config"

	return &appsv1.Deployment{
		ObjectMeta: metav1.ObjectMeta{
			Name:      name.Name,
			Namespace: name.Namespace,
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
							Name:            "flower-client",
							Image:           task.Executor.GetOciExecutor().Image,
							Args:            []string{"/dataset", "0", "localhost:9080"},
							ImagePullPolicy: corev1.PullIfNotPresent,
							VolumeMounts: []corev1.VolumeMount{
								{
									Name:      "flower-client-dataset",
									MountPath: "/dataset",
									ReadOnly:  true,
								},
							},
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
						{
							Name: "flower-client-dataset",
							VolumeSource: corev1.VolumeSource{
								HostPath: &corev1.HostPathVolumeSource{
									Path: "/dataset",
									Type: utils.HostPathTypePtr(corev1.HostPathDirectory),
								},
							},
						},
					},
					// TODO: Unhardcode secret name
					ImagePullSecrets: []corev1.LocalObjectReference{{Name: "regcred"}},
				},
			},
		},
	}
}

// Creates a new envoy proxy deployment
func NewEnvoyproxyDeployment(name types.NamespacedName) *appsv1.Deployment {
	labels := map[string]string{
		"app": name.Name,
	}

	const envoyConfigVolumeKey = "envoy-config"

	return &appsv1.Deployment{
		ObjectMeta: metav1.ObjectMeta{
			Name:      name.Name,
			Namespace: name.Namespace,
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
					Name:     "http",
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
