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

package v1alpha1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// EDIT THIS FILE!  THIS IS SCAFFOLDING FOR YOU TO OWN!
// NOTE: json tags are required.  Any new fields you add must have json tags for the fields to be serialized.

// FlEdgeSpec defines the desired state of FlEdge
type FlEdgeSpec struct {
	Auth FlEdgeAuth `json:"auth,omitempty"`
	// Important: Run "make" to regenerate code after modifying this file
}

type FlEdgeAuth struct {
	Spire *FlEdgeSpireAuth `json:"spire,omitempty"`
}
type FlEdgeSpireAuth struct {
	ServerAddress           string `json:"server-address"`
	ServerPort              int16  `json:"server-port"`
	TrustDomain             string `json:"trust-domain"`
	JoinToken               string `json:"join-token"`
	SkipKubeletVerification bool   `json:"skip-kubelet-verification,omitempty"`
	// Important: Run "make" to regenerate code after modifying this file
}

// FlEdgeStatus defines the observed state of FlEdge
type FlEdgeStatus struct {
	CurrentConfigMapName string `json:"current-configmap-name,omitempty"`
	// Important: Run "make" to regenerate code after modifying this file
}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status
//+kubebuilder:resource:scope=Cluster

// FlEdge is the Schema for the fledges API
type FlEdge struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   FlEdgeSpec   `json:"spec,omitempty"`
	Status FlEdgeStatus `json:"status,omitempty"`
}

//+kubebuilder:object:root=true

// FlEdgeList contains a list of FlEdge
type FlEdgeList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []FlEdge `json:"items"`
}

func init() {
	SchemeBuilder.Register(&FlEdge{}, &FlEdgeList{})
}
