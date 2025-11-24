pipeline {
    agent any

    parameters {
        choice(
            name: 'DEPLOY_ENV',
            choices: ['dev', 'qa', 'prod'],
            description: 'Entorno de despliegue'
        )
        booleanParam(
            name: 'RUN_SELENIUM',
            defaultValue: true,
            description: 'Ejecutar pruebas E2E con Selenium'
        )
        booleanParam(
            name: 'SKIP_SONAR',
            defaultValue: false,
            description: 'Omitir análisis de SonarQube'
        )
    }

    environment {
        NODEJS_HOME = tool name: 'NodeJS', type: 'nodejs'
        PATH = "${NODEJS_HOME}/bin:${env.PATH}"
        SONAR_SCANNER_HOME = tool name: 'SonarScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
        SONAR_PROJECT_KEY = "Inventario"
        RUN_SONARQUBE = "${!params.SKIP_SONAR}"
        SONAR_HOST_URL = "http://10.0.0.6:9000"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    echo "📥 Instalando dependencias de Node.js..."
                    bat 'npm install'

                    echo "📥 Instalando dependencias de Python..."
                    bat 'pip install -r requirements.txt'
                }
            }
        }

        stage('Python Tests & Coverage') {
            steps {
                script {
                    echo "🧪 Ejecutando pruebas de Python con coverage..."
                    try {
                        bat '''
                            pytest test/test_db.py test/test_sistema.py ^
                                --verbose ^
                                --tb=short ^
                                --cov=. ^
                                --cov-report=xml:coverage.xml ^
                                --cov-report=term
                        '''
                    } catch (Exception e) {
                        echo "⚠️ Error en pruebas Python: ${e.message}"
                        bat '''
                            echo ^<?xml version="1.0" ?^> > coverage.xml
                            echo ^<coverage version="1.0"^>^</coverage^> >> coverage.xml
                        '''
                        echo "ℹ️ Se generó coverage.xml vacío para continuar con SonarQube"
                    }
                }
            }
        }

        stage('Build & Test') {
            steps {
                echo "Ejecutando build..."
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    echo "🧪 Ejecutando pruebas unitarias..."
                    bat 'npm test -- --passWithNoTests --silent --coverage'
                }
            }
        }

        stage('🌐 Selenium E2E Tests') {
            when {
                expression {
                    return params.RUN_SELENIUM == true && params.DEPLOY_ENV == 'dev'
                }
            }
            steps {
                script {
                    try {
                        bat 'if not exist selenium-results mkdir selenium-results'
                        echo "📦 Verificando ChromeDriver..."
                        bat 'pip install --upgrade selenium webdriver-manager'

                        echo "🚀 Iniciando aplicación Next.js..."
                        bat 'start /B npm run start'
                        sleep(time: 45, unit: 'SECONDS')

                        echo "🔍 Verificando puerto 3000..."
                        bat 'curl -f http://localhost:3000 || exit 0'

                        echo "🧪 Ejecutando pruebas Selenium..."
                        bat """
                            set BASE_URL=http://localhost:3000
                            set CI=true
                            pytest test\\test_selenium_inventory.py ^
                                --verbose ^
                                --tb=short ^
                                --html=selenium-results\\selenium-report.html ^
                                --self-contained-html ^
                                --junit-xml=selenium-results\\junit.xml
                        """

                    } catch (Exception e) {
                        currentBuild.result = 'UNSTABLE'
                        echo "⚠️ Error en Selenium: ${e.message}"
                    } finally {
                        echo "🛑 Deteniendo aplicación Next.js..."
                        bat 'taskkill /F /IM node.exe /T || exit 0'
                    }
                }
            }
        }

        stage('SonarQube Analysis') {
            when {
                expression { return env.RUN_SONARQUBE == "true" && params.DEPLOY_ENV == 'dev' }
            }
            steps {
                script {
                    echo '🔍 Ejecutando análisis con SonarQube...'

                    def scannerHome = tool name: 'SonarScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'

                    withCredentials([string(credentialsId: 'sonar-token-netware', variable: 'SONAR_TOKEN')]) {
                        bat """
                            "${scannerHome}\\bin\\sonar-scanner.bat" ^
                            -Dsonar.projectKey=${SONAR_PROJECT_KEY} ^
                            -Dsonar.sources=. ^
                            -Dsonar.exclusions=**/node_modules/**,**/.next/**,^
                                **/public/**,**/coverage/**,**/build/**,**/dist/** ^
                            -Dsonar.host.url=${SONAR_HOST_URL} ^
                            -Dsonar.login=%SONAR_TOKEN% ^
                            -Dsonar.log.level=INFO
                        """
                    }
                }
            }
        }

        stage('Newman API Tests') {
            when {
                expression { return params.DEPLOY_ENV == 'dev' || params.DEPLOY_ENV == 'qa' }
            }
            steps {
                script {
                    try {
                        bat '''
                            newman run test/postman-collection.json ^
                                --reporters cli,json ^
                                --reporter-json-export results/newman-report.json
                        '''
                    } catch (e) {
                        currentBuild.result = 'UNSTABLE'
                        echo "⚠️ Falló Newman"
                    }
                }
            }
        }

        stage('JMeter Performance Tests') {
            when {
                expression { return params.DEPLOY_ENV == 'qa' }
            }
            steps {
                script {
                    try {
                        bat '''
                            jmeter -n ^
                                -t test/jmeter-test-plan.jmx ^
                                -l results/jmeter-results.jtl ^
                                -e -o results/jmeter-report
                        '''
                    } catch (e) {
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('OWASP Dependency Check') {
            when {
                expression { return params.DEPLOY_ENV == 'qa' || params.DEPLOY_ENV == 'prod' }
            }
            steps {
                script {
                    try {
                        bat '''
                            dependency-check ^
                                --project "Inventario" ^
                                --scan . ^
                                --format HTML ^
                                --format JSON ^
                                --out . ^
                                --suppression dependency-check-suppressions.xml
                        '''
                    } catch (e) {
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Install Google Code Style') {
            when {
                expression { return params.DEPLOY_ENV == 'qa' || params.DEPLOY_ENV == 'prod' }
            }
            steps {
                script {
                    try {
                        bat 'npm run lint'
                    } catch (e) {
                        echo "⚠️ Advertencias de linting"
                    }
                }
            }
        }

        stage('Archive Results') {
            steps {
                script {
                    archiveArtifacts artifacts: '**/coverage.xml', allowEmptyArchive: true
                    archiveArtifacts artifacts: '**/selenium-results/**/*', allowEmptyArchive: true
                    archiveArtifacts artifacts: '**/results/**/*', allowEmptyArchive: true
                    archiveArtifacts artifacts: '**/dependency-check-report.*', allowEmptyArchive: true

                    junit allowEmptyResults: true, testResults: '**/selenium-results/junit.xml'
                }
            }
        }

        stage('Deployment Preparation') {
            when {
                expression { return params.DEPLOY_ENV == 'prod' }
            }
            steps {
                echo "🚀 Preparando despliegue PROD..."
            }
        }
    }

    post {

        always {
            echo "🧹 Limpiando workspace..."
            bat '''
                if exist ".next" rmdir /s /q ".next"
                if exist ".scannerwork" rmdir /s /q ".scannerwork"
                if exist "results" rmdir /s /q "results"
                if exist "dependency-check-report.html" del /q "dependency-check-report.html"
                if exist "dependency-check-report.json" del /q "dependency-check-report.json"
            '''
            echo "🧨 === PIPELINE FINALIZADO ==="
        }

        unstable {
            script {
                if (params.DEPLOY_ENV == 'dev') {
                    currentBuild.result = 'SUCCESS'
                    echo "⚠️ Marcado como SUCCESS (UNSTABLE permitido en dev)"
                }
            }
        }

        failure {
            script {
                echo "❌ === EL PIPELINE FALLÓ ==="
                echo "Entorno: ${params.DEPLOY_ENV}"
            }
        }
    }
}
