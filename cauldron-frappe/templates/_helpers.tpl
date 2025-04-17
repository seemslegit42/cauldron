{{/*
Expand the name of the chart.
*/}}
{{- define "cauldron-frappe.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "cauldron-frappe.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "cauldron-frappe.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "cauldron-frappe.labels" -}}
helm.sh/chart: {{ include "cauldron-frappe.chart" . }}
{{ include "cauldron-frappe.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.global.labels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "cauldron-frappe.selectorLabels" -}}
app.kubernetes.io/name: {{ include "cauldron-frappe.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "cauldron-frappe.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "cauldron-frappe.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Web component name
*/}}
{{- define "cauldron-frappe.web.name" -}}
{{- printf "%s-web" (include "cauldron-frappe.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Worker component name
*/}}
{{- define "cauldron-frappe.worker.name" -}}
{{- printf "%s-worker" (include "cauldron-frappe.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Scheduler component name
*/}}
{{- define "cauldron-frappe.scheduler.name" -}}
{{- printf "%s-scheduler" (include "cauldron-frappe.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Socket.IO component name
*/}}
{{- define "cauldron-frappe.socketio.name" -}}
{{- printf "%s-socketio" (include "cauldron-frappe.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Data volume name
*/}}
{{- define "cauldron-frappe.pvc.name" -}}
{{- printf "%s-data" (include "cauldron-frappe.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Config map name
*/}}
{{- define "cauldron-frappe.configmap.name" -}}
{{- printf "%s-config" (include "cauldron-frappe.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
