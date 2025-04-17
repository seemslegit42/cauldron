{{/*
Expand the name of the chart.
*/}}
{{- define "cauldron-infra.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "cauldron-infra.fullname" -}}
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
{{- define "cauldron-infra.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "cauldron-infra.labels" -}}
helm.sh/chart: {{ include "cauldron-infra.chart" . }}
{{ include "cauldron-infra.selectorLabels" . }}
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
{{- define "cauldron-infra.selectorLabels" -}}
app.kubernetes.io/name: {{ include "cauldron-infra.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "cauldron-infra.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "cauldron-infra.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
TimescaleDB fullname
*/}}
{{- define "timescaledb.fullname" -}}
{{- printf "%s-timescaledb" (include "cauldron-infra.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Qdrant fullname
*/}}
{{- define "qdrant.fullname" -}}
{{- printf "%s-qdrant" (include "cauldron-infra.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Redis Cache fullname
*/}}
{{- define "redis-cache.fullname" -}}
{{- printf "%s-redis-cache" (include "cauldron-infra.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Redis Queue fullname
*/}}
{{- define "redis-queue.fullname" -}}
{{- printf "%s-redis-queue" (include "cauldron-infra.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Redis SocketIO fullname
*/}}
{{- define "redis-socketio.fullname" -}}
{{- printf "%s-redis-socketio" (include "cauldron-infra.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
