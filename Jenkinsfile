pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    environment {
        PATH = "${env.HOME}/.local/bin:${env.PATH}"
        UV_LINK_MODE = 'copy'
    }

    stages {
        stage('Instalar dependencias') {
            steps {
                sh 'uv sync --group dev'
                sh 'cd frontend && npm ci'
                sh 'uv run playwright install chromium'
            }
        }

        stage('Lint') {
            parallel {
                stage('ruff') {
                    steps { sh 'uv run ruff check .' }
                }
                stage('eslint') {
                    steps { sh 'cd frontend && npm run lint' }
                }
            }
        }

        stage('Unit + Integration') {
            steps {
                sh 'uv run pytest tests/unit tests/integration -m "not e2e" --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80 --junitxml=reports/junit-unit.xml'
            }
        }

        stage('Build frontend') {
            steps { sh 'cd frontend && npm run build' }
        }

        stage('E2E (Playwright)') {
            steps {
                sh 'uv run pytest tests/e2e -m e2e --html=playwright-report/index.html --self-contained-html --junitxml=reports/junit-e2e.xml --tracing retain-on-failure --screenshot only-on-failure --output test-results'
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'reports/*.xml'
            archiveArtifacts artifacts: 'htmlcov/**, playwright-report/**, test-results/**', allowEmptyArchive: true
        }
    }
}
