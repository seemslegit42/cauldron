{{/*
Expand the name of the chart.
*/}}
{{- define "cauldron-nextcloud.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "cauldron-nextcloud.fullname" -}}
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
{{- define "cauldron-nextcloud.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "cauldron-nextcloud.labels" -}}
helm.sh/chart: {{ include "cauldron-nextcloud.chart" . }}
{{ include "cauldron-nextcloud.selectorLabels" . }}
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
{{- define "cauldron-nextcloud.selectorLabels" -}}
app.kubernetes.io/name: {{ include "cauldron-nextcloud.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "cauldron-nextcloud.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "cauldron-nextcloud.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the config map to use
*/}}
{{- define "cauldron-nextcloud.configMapName" -}}
{{- printf "%s-config" (include "cauldron-nextcloud.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create the name of the secret to use
*/}}
{{- define "cauldron-nextcloud.secretName" -}}
{{- if .Values.nextcloud.admin.existingSecret }}
{{- .Values.nextcloud.admin.existingSecret }}
{{- else }}
{{- printf "%s-secret" (include "cauldron-nextcloud.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Create the name of the PVC to use
*/}}
{{- define "cauldron-nextcloud.pvcName" -}}
{{- printf "%s-data" (include "cauldron-nextcloud.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
