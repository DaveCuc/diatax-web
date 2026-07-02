# Credentials Configuration - diatax-web

This document explains the two available options to authenticate and configure credentials in the local development environment using ADK 2.0.

---

## Option A: Authentication via Google AI Studio (API Key)

This is the fastest method for local prototyping.

1. **Obtain API Key:**
   Generate your API key directly in the official Google AI Studio console:
   👉 [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

2. **Local Configuration:**
   Create or edit your `.env` file in the project root and add your key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
   *Note: Ensure Vertex AI variables (`GOOGLE_GENAI_USE_VERTEXAI`) are commented out or removed for the SDK to use AI Studio by default.*

---

## Option B: Authentication via Google Cloud (Vertex AI)

Recommended for enterprise-grade environments and production deployments.

1. **Install Google Cloud SDK:**
   Make sure you have the [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed.

2. **Login and Local Credentials (ADC):**
   Run the following command in your terminal to authorize your local environment using Application Default Credentials (ADC):
   ```bash
   gcloud auth application-default login
   ```

3. **Configure Quota Project (Important):**
   To avoid billing or quota errors (such as `Permission denied on resource project None`), login by explicitly linking your Google Cloud Project ID as the quota project:
   ```bash
   gcloud auth application-default login --update-quota-project YOUR_PROJECT_ID_HERE
   ```

4. **Environment Variables:**
   Configure your `.env` file with the corresponding Google Cloud project details:
   ```env
   GOOGLE_GENAI_USE_VERTEXAI=true
   GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID_HERE
   GOOGLE_CLOUD_LOCATION=global
   ```
