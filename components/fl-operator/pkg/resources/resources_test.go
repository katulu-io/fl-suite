package resources_test

import (
	"testing"

	v1alpha1 "github.com/katulu-io/fl-suite/fl-operator/api/v1alpha1"
	. "github.com/onsi/gomega"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	"github.com/katulu-io/fl-suite/fl-operator/pkg/resources"
	pb "github.com/katulu-io/fl-suite/fl-orchestrator/pkg/api/fl_orchestrator/v1"
	"k8s.io/apimachinery/pkg/types"
)

func TestNewPodWithRegistryCredentials(t *testing.T) {
	g := NewGomegaWithT(t)

	ociExecutor := &pb.OrchestratorMessage_ExecutorSpec_OciExecutor{
		OciExecutor: &pb.OrchestratorMessage_ExecutorSpec_OCIExecutorSpec{
			Image: "flower-client:latest",
		},
	}
	task := &pb.OrchestratorMessage_TaskSpec{
		ID: "an-id",
		Executor: &pb.OrchestratorMessage_ExecutorSpec{
			Executor: ociExecutor,
		},
	}
	podName := types.NamespacedName{
		Name:      "test",
		Namespace: "test",
	}
	registryCredentials := &v1alpha1.FlOperatorRegistryCredentials{
		Secret: "regcred",
	}

	pod := resources.NewPod(task, podName, "test-envoy-config", registryCredentials)

	shareProcessNamespace := true
	spireAgentSockeVolumeType := corev1.HostPathDirectoryOrCreate
	expectedPod := &corev1.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name:      "test",
			Namespace: "test",
			Labels: map[string]string{
				"app":            "flower-client",
				"run-id":         "an-id",
				"spire-workload": "flower-client",
			},
		},
		Spec: corev1.PodSpec{
			ShareProcessNamespace: &shareProcessNamespace,
			Containers: []corev1.Container{
				{
					Name:            "flower-client",
					Image:           "flower-client:latest",
					ImagePullPolicy: "IfNotPresent",
					Command:         []string{"/bin/bash", "-c"},
					Args:            []string{"python /app/main.py && pkill envoy"},
				},
				{
					Name:            "envoyproxy",
					Image:           "envoyproxy/envoy:v1.20-latest",
					ImagePullPolicy: "IfNotPresent",
					Args:            []string{"-l", "debug", "--local-address-ip-version", "v4", "-c", "/run/envoy/envoy.yaml", "--base-id", "1"},
					Ports: []corev1.ContainerPort{
						{
							ContainerPort: 9080,
						},
					},
					VolumeMounts: []corev1.VolumeMount{
						{
							Name:      "envoy-config",
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
			RestartPolicy: "OnFailure",
			Volumes: []corev1.Volume{
				{
					Name: "envoy-config",
					VolumeSource: corev1.VolumeSource{
						ConfigMap: &corev1.ConfigMapVolumeSource{
							LocalObjectReference: corev1.LocalObjectReference{
								Name: "test-envoy-config",
							},
						},
					},
				},
				{
					Name: "spire-agent-socket",
					VolumeSource: corev1.VolumeSource{
						HostPath: &corev1.HostPathVolumeSource{
							Path: "/run/spire/sockets",
							Type: &spireAgentSockeVolumeType,
						},
					},
				},
			},
			ImagePullSecrets: []corev1.LocalObjectReference{{Name: "regcred"}},
		},
	}

	g.Expect(pod).To(Equal(expectedPod), "Pod doesn't match")
}

func TestNewPodWithoutRegistryCredentials(t *testing.T) {
	g := NewGomegaWithT(t)

	ociExecutor := &pb.OrchestratorMessage_ExecutorSpec_OciExecutor{
		OciExecutor: &pb.OrchestratorMessage_ExecutorSpec_OCIExecutorSpec{
			Image: "flower-client:latest",
		},
	}
	task := &pb.OrchestratorMessage_TaskSpec{
		ID: "an-id",
		Executor: &pb.OrchestratorMessage_ExecutorSpec{
			Executor: ociExecutor,
		},
	}
	podName := types.NamespacedName{
		Name:      "test",
		Namespace: "test",
	}

	pod := resources.NewPod(task, podName, "test-envoy-config", nil)

	shareProcessNamespace := true
	spireAgentSockeVolumeType := corev1.HostPathDirectoryOrCreate
	expectedPod := &corev1.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name:      "test",
			Namespace: "test",
			Labels: map[string]string{
				"app":            "flower-client",
				"run-id":         "an-id",
				"spire-workload": "flower-client",
			},
		},
		Spec: corev1.PodSpec{
			ShareProcessNamespace: &shareProcessNamespace,
			Containers: []corev1.Container{
				{
					Name:            "flower-client",
					Image:           "flower-client:latest",
					ImagePullPolicy: "IfNotPresent",
					Command:         []string{"/bin/bash", "-c"},
					Args:            []string{"python /app/main.py && pkill envoy"},
				},
				{
					Name:            "envoyproxy",
					Image:           "envoyproxy/envoy:v1.20-latest",
					ImagePullPolicy: "IfNotPresent",
					Args:            []string{"-l", "debug", "--local-address-ip-version", "v4", "-c", "/run/envoy/envoy.yaml", "--base-id", "1"},
					Ports: []corev1.ContainerPort{
						{
							ContainerPort: 9080,
						},
					},
					VolumeMounts: []corev1.VolumeMount{
						{
							Name:      "envoy-config",
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
			RestartPolicy: "OnFailure",
			Volumes: []corev1.Volume{
				{
					Name: "envoy-config",
					VolumeSource: corev1.VolumeSource{
						ConfigMap: &corev1.ConfigMapVolumeSource{
							LocalObjectReference: corev1.LocalObjectReference{
								Name: "test-envoy-config",
							},
						},
					},
				},
				{
					Name: "spire-agent-socket",
					VolumeSource: corev1.VolumeSource{
						HostPath: &corev1.HostPathVolumeSource{
							Path: "/run/spire/sockets",
							Type: &spireAgentSockeVolumeType,
						},
					},
				},
			},
		},
	}

	g.Expect(pod).To(Equal(expectedPod), "Pod doesn't match")
}
