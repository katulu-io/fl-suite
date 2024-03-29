//go:build !ignore_autogenerated
// +build !ignore_autogenerated

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

// Code generated by controller-gen. DO NOT EDIT.

package v1alpha1

import (
	runtime "k8s.io/apimachinery/pkg/runtime"
)

// DeepCopyInto is an autogenerated deepcopy function, copying the receiver, writing into out. in must be non-nil.
func (in *FlEdge) DeepCopyInto(out *FlEdge) {
	*out = *in
	out.TypeMeta = in.TypeMeta
	in.ObjectMeta.DeepCopyInto(&out.ObjectMeta)
	in.Spec.DeepCopyInto(&out.Spec)
	out.Status = in.Status
}

// DeepCopy is an autogenerated deepcopy function, copying the receiver, creating a new FlEdge.
func (in *FlEdge) DeepCopy() *FlEdge {
	if in == nil {
		return nil
	}
	out := new(FlEdge)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyObject is an autogenerated deepcopy function, copying the receiver, creating a new runtime.Object.
func (in *FlEdge) DeepCopyObject() runtime.Object {
	if c := in.DeepCopy(); c != nil {
		return c
	}
	return nil
}

// DeepCopyInto is an autogenerated deepcopy function, copying the receiver, writing into out. in must be non-nil.
func (in *FlEdgeAuth) DeepCopyInto(out *FlEdgeAuth) {
	*out = *in
	if in.Spire != nil {
		in, out := &in.Spire, &out.Spire
		*out = new(FlEdgeSpireAuth)
		**out = **in
	}
}

// DeepCopy is an autogenerated deepcopy function, copying the receiver, creating a new FlEdgeAuth.
func (in *FlEdgeAuth) DeepCopy() *FlEdgeAuth {
	if in == nil {
		return nil
	}
	out := new(FlEdgeAuth)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyInto is an autogenerated deepcopy function, copying the receiver, writing into out. in must be non-nil.
func (in *FlEdgeList) DeepCopyInto(out *FlEdgeList) {
	*out = *in
	out.TypeMeta = in.TypeMeta
	in.ListMeta.DeepCopyInto(&out.ListMeta)
	if in.Items != nil {
		in, out := &in.Items, &out.Items
		*out = make([]FlEdge, len(*in))
		for i := range *in {
			(*in)[i].DeepCopyInto(&(*out)[i])
		}
	}
}

// DeepCopy is an autogenerated deepcopy function, copying the receiver, creating a new FlEdgeList.
func (in *FlEdgeList) DeepCopy() *FlEdgeList {
	if in == nil {
		return nil
	}
	out := new(FlEdgeList)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyObject is an autogenerated deepcopy function, copying the receiver, creating a new runtime.Object.
func (in *FlEdgeList) DeepCopyObject() runtime.Object {
	if c := in.DeepCopy(); c != nil {
		return c
	}
	return nil
}

// DeepCopyInto is an autogenerated deepcopy function, copying the receiver, writing into out. in must be non-nil.
func (in *FlEdgeSpec) DeepCopyInto(out *FlEdgeSpec) {
	*out = *in
	in.Auth.DeepCopyInto(&out.Auth)
}

// DeepCopy is an autogenerated deepcopy function, copying the receiver, creating a new FlEdgeSpec.
func (in *FlEdgeSpec) DeepCopy() *FlEdgeSpec {
	if in == nil {
		return nil
	}
	out := new(FlEdgeSpec)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyInto is an autogenerated deepcopy function, copying the receiver, writing into out. in must be non-nil.
func (in *FlEdgeSpireAuth) DeepCopyInto(out *FlEdgeSpireAuth) {
	*out = *in
}

// DeepCopy is an autogenerated deepcopy function, copying the receiver, creating a new FlEdgeSpireAuth.
func (in *FlEdgeSpireAuth) DeepCopy() *FlEdgeSpireAuth {
	if in == nil {
		return nil
	}
	out := new(FlEdgeSpireAuth)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyInto is an autogenerated deepcopy function, copying the receiver, writing into out. in must be non-nil.
func (in *FlEdgeStatus) DeepCopyInto(out *FlEdgeStatus) {
	*out = *in
}

// DeepCopy is an autogenerated deepcopy function, copying the receiver, creating a new FlEdgeStatus.
func (in *FlEdgeStatus) DeepCopy() *FlEdgeStatus {
	if in == nil {
		return nil
	}
	out := new(FlEdgeStatus)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyInto is an autogenerated deepcopy function, copying the receiver, writing into out. in must be non-nil.
func (in *FlOperator) DeepCopyInto(out *FlOperator) {
	*out = *in
	out.TypeMeta = in.TypeMeta
	in.ObjectMeta.DeepCopyInto(&out.ObjectMeta)
	in.Spec.DeepCopyInto(&out.Spec)
	out.Status = in.Status
}

// DeepCopy is an autogenerated deepcopy function, copying the receiver, creating a new FlOperator.
func (in *FlOperator) DeepCopy() *FlOperator {
	if in == nil {
		return nil
	}
	out := new(FlOperator)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyObject is an autogenerated deepcopy function, copying the receiver, creating a new runtime.Object.
func (in *FlOperator) DeepCopyObject() runtime.Object {
	if c := in.DeepCopy(); c != nil {
		return c
	}
	return nil
}

// DeepCopyInto is an autogenerated deepcopy function, copying the receiver, writing into out. in must be non-nil.
func (in *FlOperatorList) DeepCopyInto(out *FlOperatorList) {
	*out = *in
	out.TypeMeta = in.TypeMeta
	in.ListMeta.DeepCopyInto(&out.ListMeta)
	if in.Items != nil {
		in, out := &in.Items, &out.Items
		*out = make([]FlOperator, len(*in))
		for i := range *in {
			(*in)[i].DeepCopyInto(&(*out)[i])
		}
	}
}

// DeepCopy is an autogenerated deepcopy function, copying the receiver, creating a new FlOperatorList.
func (in *FlOperatorList) DeepCopy() *FlOperatorList {
	if in == nil {
		return nil
	}
	out := new(FlOperatorList)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyObject is an autogenerated deepcopy function, copying the receiver, creating a new runtime.Object.
func (in *FlOperatorList) DeepCopyObject() runtime.Object {
	if c := in.DeepCopy(); c != nil {
		return c
	}
	return nil
}

// DeepCopyInto is an autogenerated deepcopy function, copying the receiver, writing into out. in must be non-nil.
func (in *FlOperatorRegistryCredentials) DeepCopyInto(out *FlOperatorRegistryCredentials) {
	*out = *in
}

// DeepCopy is an autogenerated deepcopy function, copying the receiver, creating a new FlOperatorRegistryCredentials.
func (in *FlOperatorRegistryCredentials) DeepCopy() *FlOperatorRegistryCredentials {
	if in == nil {
		return nil
	}
	out := new(FlOperatorRegistryCredentials)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyInto is an autogenerated deepcopy function, copying the receiver, writing into out. in must be non-nil.
func (in *FlOperatorSpec) DeepCopyInto(out *FlOperatorSpec) {
	*out = *in
	if in.RegistryCredentials != nil {
		in, out := &in.RegistryCredentials, &out.RegistryCredentials
		*out = new(FlOperatorRegistryCredentials)
		**out = **in
	}
}

// DeepCopy is an autogenerated deepcopy function, copying the receiver, creating a new FlOperatorSpec.
func (in *FlOperatorSpec) DeepCopy() *FlOperatorSpec {
	if in == nil {
		return nil
	}
	out := new(FlOperatorSpec)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyInto is an autogenerated deepcopy function, copying the receiver, writing into out. in must be non-nil.
func (in *FlOperatorStatus) DeepCopyInto(out *FlOperatorStatus) {
	*out = *in
}

// DeepCopy is an autogenerated deepcopy function, copying the receiver, creating a new FlOperatorStatus.
func (in *FlOperatorStatus) DeepCopy() *FlOperatorStatus {
	if in == nil {
		return nil
	}
	out := new(FlOperatorStatus)
	in.DeepCopyInto(out)
	return out
}
