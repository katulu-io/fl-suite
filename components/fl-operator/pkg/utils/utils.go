package utils

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"

	corev1 "k8s.io/api/core/v1"
	v1 "k8s.io/api/core/v1"
)

func Int32Ptr(i int32) *int32 {
	return &i
}

func HostPathTypePtr(t v1.HostPathType) *v1.HostPathType {
	return &t
}

// Inspired by kustomize: https://github.com/kubernetes-sigs/kustomize/blob/master/api/hasher/hasher.go#L60
func HashConfigMap(cm *corev1.ConfigMap) (string, error) {
	encoded, err := encodeConfigMap(cm)
	if err != nil {
		return "", err
	}
	return encode(hex256(encoded))
}

// Inspired by kustomize: https://github.com/kubernetes-sigs/kustomize/blob/master/api/hasher/hasher.go#L109
func encodeConfigMap(cm *corev1.ConfigMap) (string, error) {
	// get fields
	m := map[string]interface{}{
		"kind": "ConfigMap",
		"name": cm.GetName(),
		"data": cm.Data,
	}

	// json.Marshal sorts the keys in a stable order in the encoding
	data, err := json.Marshal(m)
	if err != nil {
		return "", err
	}

	return string(data), nil
}

// Taken from kustomize: https://github.com/kubernetes-sigs/kustomize/blob/master/api/hasher/hasher.go#L28
// Which in turn is taken from: https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/kubectl/pkg/util/hash/hash.go#L105
func encode(hex string) (string, error) {
	if len(hex) < 10 {
		return "", fmt.Errorf(
			"input length must be at least 10")
	}
	enc := []rune(hex[:10])
	for i := range enc {
		switch enc[i] {
		case '0':
			enc[i] = 'g'
		case '1':
			enc[i] = 'h'
		case '3':
			enc[i] = 'k'
		case 'a':
			enc[i] = 'm'
		case 'e':
			enc[i] = 't'
		}
	}
	return string(enc), nil
}

// Taken from kustomize: https://github.com/kubernetes-sigs/kustomize/blob/master/api/hasher/hasher.go#L52
func hex256(data string) string {
	return fmt.Sprintf("%x", sha256.Sum256([]byte(data)))
}
