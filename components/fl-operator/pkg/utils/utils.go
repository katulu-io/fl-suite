package utils

import (
	v1 "k8s.io/api/core/v1"
)

func Int32Ptr(i int32) *int32 {
	return &i
}

func HostPathTypePtr(t v1.HostPathType) *v1.HostPathType {
	return &t
}
