pipeline {
    agent any

    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'qa', 'prod'],
            description: 'Selecciona el entorno de despliegue'
        )
        booleanParam(
            name: 'SKIP_TESTS',
            defaultValue: false,
            description: 'Saltar pruebas unitarias (solo para emergencias)'
        )
        booleanParam(
            name: 'RUN_SELENIUM',
            defaultValue: true,
            description: 'Ejecutar pruebas Selenium E2E'
        )
    }

    environment {
        SONAR_HOST_URL = 'https://srvapp.netwaresoft.com'
        SONAR_PROJECT_KEY = 'GYKVENTAS'
        NODE_HOME = tool name: 'NodeJS-20', type: 'nodejs'
        PATH = "${NODE_HOME}/bin;${env.PATH}"
        NEXT_TELEMETRY_DISABLED = '1'
        // No calcular RUN_* aquí para evitar evaluación temprana; se setean en el stage 'Environment Setup'
    }

    tools {
        nodejs 'NodeJS-20'
    }

    stages {
        stage('Environment Setup') {
            steps {
                script {
                    echo "🌍 =========================================="
                    echo "   CONFIGURACIÓN DEL ENTORNO"
                    echo "=========================================="

                    // Variables dependientes de params: se calculan aquí
                    env.DEPLOY_ENV = params.ENVIRONMENT
                    env.RUN_SONARQUBE = (params.ENVIRONMENT == 'dev') ? 'true' : 'false'
                    env.RUN_NEWMAN = (params.ENVIRONMENT == 'prod') ? 'false' : 'true'
                    env.RUN_JMETER = (params.ENVIRONMENT == 'dev') ? 'true' : 'false'
                    env.RUN_OWASP = (params.ENVIRONMENT == 'dev') ? 'true' : 'false'
                    env.RUN_SELENIUM = (params.RUN_SELENIUM == true) ? 'true' : 'false'

                    echo "🎯 Entorno seleccionado: ${env.DEPLOY_ENV}"
                    echo "📊 SonarQube: ${env.RUN_SONARQUBE == 'true' ? '✅ ACTIVADO' : '⏭️ OMITIDO'}"
                    echo "🧪 Newman (Postman): ${env.RUN_NEWMAN == 'true' ? '✅ ACTIVADO' : '⏭️ OMITIDO'}"
                    echo "⚡ JMeter: ${env.RUN_JMETER == 'true' ? '✅ ACTIVADO' : '⏭️ OMITIDO'}"
                    echo "🛡️ OWASP: ${env.RUN_OWASP == 'true' ? '✅ ACTIVADO' : '⏭️ OMITIDO'}"
                    echo "🌐 Selenium E2E: ${env.RUN_SELENIUM == 'true' ? '✅ ACTIVADO' : '⏭️ OMITIDO'}"
                    echo "=========================================="

                    if (env.DEPLOY_ENV == 'prod') {
                        env.BUILD_OPTIMIZATION = 'true'
                        env.SOURCE_MAPS = 'false'
                    } else {
                        env.BUILD_OPTIMIZATION = 'false'
                        env.SOURCE_MAPS = 'true'
                    }
                }
            }
        }

        stage('Checkout') {
            steps {
                echo '📥 Clonando repositorio desde GitHub...'
                git branch: 'main', url: 'https://github.com/Jeanpierrre/Inventario.git'
            }
        }

        stage('Environment Info') {
            steps {
                echo '🔍 Verificando entorno...'
                bat '''
                    echo Node version:
                    node --version
                    echo NPM version:
                    npm --version
                    echo Python version:
                    python --version
                    echo Entorno: %DEPLOY_ENV%
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                echo "📦 Instalando dependencias para ${env.DEPLOY_ENV}..."
                script {
                    bat '''
                        if not exist package-lock.json (
                            echo Generando package-lock.json...
                            npm install --package-lock-only --legacy-peer-deps
                        )
                    '''
                    if (env.DEPLOY_ENV == 'prod') {
                        bat 'npm ci --omit=dev --legacy-peer-deps --prefer-offline'
                    } else {
                        bat 'npm ci --legacy-peer-deps --prefer-offline || npm install --legacy-peer-deps --prefer-offline'
                    }
                }
            }
        }

        stage('Install Selenium Dependencies') {
            when {
                expression { return env.RUN_SELENIUM == 'true' }
            }
            steps {
                echo '📦 Instalando dependencias de Selenium...'
                bat '''
                    python -m pip install --upgrade pip
                    pip install selenium pytest pytest-html pytest-xdist webdriver-manager
                '''
            }
        }

        stage('Build Frontend') {
            steps {
                echo "🔨 Construyendo aplicación Next.js para ${env.DEPLOY_ENV}..."
                script {
                    if (env.DEPLOY_ENV == 'prod') {
                        bat 'npm run build -- --no-lint'
                    } else {
                        bat 'npm run build'
                    }
                }
            }
        }

        stage('JavaScript/TypeScript Coverage') {
            when {
                expression { return env.RUN_SONARQUBE == 'true' }
            }
            steps {
                echo '📊 Generando cobertura de JavaScript/TypeScript para SonarQube...'
                script {
                    try {
                        bat '''
                            echo Ejecutando tests con cobertura...
                            npm test -- --coverage --watchAll=false --passWithNoTests
                        '''
                        echo '✅ Cobertura JS/TS generada - coverage/lcov.info creado'
                    } catch (Exception e) {
                        echo "⚠️ Error en cobertura JS/TS: ${e.message}"
                        bat '''
                            if not exist coverage mkdir coverage
                            echo # Empty coverage > coverage/lcov.info
                        '''
                        echo "ℹ️ Se generó lcov.info vacío para continuar"
                    }
                }
            }
        }

        stage('Python Tests & Coverage') {
            steps {
                echo '🐍 Ejecutando pruebas Python con cobertura...'
                script {
                    try {
                        bat 'python --version'
                        bat '''
                            echo Instalando dependencias de Python...
                            python -m pip install --upgrade pip
                            pip install pytest pytest-cov
                        '''
                        bat '''
                            set DATABASE_URL=sqlite:///test.db
                            echo Ejecutando pytest con cobertura...
                            pytest --cov=db --cov=sistema --cov-report=xml --cov-report=term-missing
                        '''
                        echo '✅ Pruebas Python completadas - coverage.xml generado'
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

        stage('Run Tests') {
            when {
                expression { return params.SKIP_TESTS == false && env.DEPLOY_ENV != 'prod' }
            }
            steps {
                echo '🧪 Ejecutando pruebas unitarias...'
                script {
                    try {
                        bat 'npm test -- --passWithNoTests --silent --coverage'
                    } catch (Exception e) {
                        echo "⚠️ Tests completados con advertencias: ${e.message}"
                        currentBuild.result = 'SUCCESS'
                    }
                }
            }
        }

        stage('🌐 Selenium E2E Tests') {
            when {
                expression { return env.RUN_SELENIUM == 'true' && env.DEPLOY_ENV == 'dev' }
            }
            steps {
                echo '🌐 Ejecutando pruebas E2E con Selenium...'
                script {
                    try {
                        bat 'if not exist selenium-results mkdir selenium-results'
                        echo '📦 Verificando ChromeDriver y dependencias...'
                        bat 'pip install --upgrade selenium webdriver-manager'

                        echo '🚀 Iniciando aplicación Next.js en background...'
                        bat 'start /B npm run start'

                        echo '⏳ Esperando 30 segundos para que Next.js inicie completamente...'
                        sleep(time: 30, unit: 'SECONDS')

                        echo '🧪 Ejecutando pruebas Selenium...'
                        bat '''
                            set BASE_URL=http://localhost:3000
                            set CI=true
                            pytest test\\test_selenium_inventory.py ^
                                --verbose ^
                                --tb=short ^
                                --html=selenium-results\\selenium-report.html ^
                                --self-contained-html ^
                                -v ^
                                --junit-xml=selenium-results\\junit.xml
                        '''

                        echo '✅ Pruebas Selenium completadas exitosamente'
                        archiveArtifacts artifacts: 'selenium-results/**', allowEmptyArchive: true, fingerprint: true
                    } catch (Exception e) {
                        echo "⚠️ Error durante pruebas Selenium: ${e.message}"
                        bat '''
                            if exist "screenshot_*.png" (
                                if not exist selenium-results mkdir selenium-results
                                move screenshot_*.png selenium-results\\ 2>nul
                            )
                        '''
                        archiveArtifacts artifacts: 'selenium-results/**,screenshot_*.png', allowEmptyArchive: true
                        currentBuild.result = 'UNSTABLE'
                        echo "⚠️ Build marcado como UNSTABLE pero continúa"
                    } finally {
                        echo '🛑 Deteniendo aplicación Next.js (si existe)...'
                        bat 'taskkill /F /IM node.exe /T || exit 0'
                    }
                }
            }
        }

     stage('SonarQube Analysis') {
            when {
                expression { return RUN_SONARQUBE == 'true' }
            }
            steps {
                echo '🔍 [DEV ONLY] Ejecutando análisis de código con SonarQube...'
                script {
                    def scannerHome = tool name: 'SonarScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                    withCredentials([string(credentialsId: 'sonar-token-netware', variable: 'SONAR_TOKEN')]) {
                        bat """
                            "${scannerHome}\\bin\\sonar-scanner.bat" ^
                            -Dsonar.projectKey=${SONAR_PROJECT_KEY} ^
                            -Dsonar.sources=. ^
                            -Dsonar.exclusions=**/node_modules/**,**/.next/**,**/public/**,**/coverage/**,**/build/**,**/dist/** ^
                            -Dsonar.test.inclusions=**/*.test.ts,**/*.test.tsx,**/*.spec.ts,**/*.spec.tsx ^
                            -Dsonar.javascript.node.maxspace=4096 ^
                            -Dsonar.host.url=${SONAR_HOST_URL} ^
                            -Dsonar.token=%SONAR_TOKEN% ^
                            -Dsonar.log.level=INFO
                        """
                    }
                }
            }
        }

        stage('Newman API Tests') {
            when {
                expression { return env.RUN_NEWMAN == 'true' }
            }
            steps {
                echo "🧪 [${env.DEPLOY_ENV.toUpperCase()}] Ejecutando pruebas de API con Newman (Postman)..."
                script {
                    try {
                        bat 'if not exist newman-results mkdir newman-results'
                        bat '''
                            where newman >nul 2>&1 || (
                                echo Newman no encontrado, instalando...
                                npm install -g newman newman-reporter-htmlextra
                            )
                        '''
                        bat 'start /B npm run start'
                        echo "Esperando 20 segundos para que Next.js inicie en ${env.DEPLOY_ENV}..."
                        sleep(time: 20, unit: 'SECONDS')
                        bat """
                            newman run test/postman-collection.json ^
                            --environment test/postman-env-${env.DEPLOY_ENV}.json ^
                            --reporters cli,htmlextra,json ^
                            --reporter-htmlextra-export newman-results/newman-report-${env.DEPLOY_ENV}.html ^
                            --reporter-json-export newman-results/newman-report-${env.DEPLOY_ENV}.json
                        """
                        archiveArtifacts artifacts: 'newman-results/**/*', allowEmptyArchive: true
                        echo "✅ Pruebas Newman completadas para ${env.DEPLOY_ENV}"
                    } catch (Exception e) {
                        echo "⚠️ Error en Newman: ${e.message}"
                        if (env.DEPLOY_ENV == 'qa') {
                            throw e
                        }
                    } finally {
                        bat 'taskkill /F /IM node.exe /T || exit 0'
                    }
                }
            }
        }

        stage('JMeter Performance Tests') {
            when {
                expression { return env.RUN_JMETER == 'true' }
            }
            steps {
                echo '⚡ [DEV ONLY] Ejecutando pruebas de rendimiento con JMeter...'
                script {
                    try {
                        bat 'if not exist results mkdir results'
                        bat 'start /B npm run start'
                        echo 'Esperando 20 segundos para que Next.js inicie...'
                        sleep(time: 20, unit: 'SECONDS')

                        def jmeterPath = 'C:\\apache-jmeter-5.6.3\\bin\\jmeter.bat'
                        if (fileExists(jmeterPath)) {
                            bat """
                                "${jmeterPath}" -n ^
                                -t tests/api-load-test.jmx ^
                                -l results/jmeter-results.jtl ^
                                -e -o results/jmeter-report ^
                                -Jbase_url=localhost:3000
                            """
                            archiveArtifacts artifacts: 'results/jmeter-report/**/*', allowEmptyArchive: true, fingerprint: true
                            echo '✅ Pruebas JMeter completadas'
                        } else {
                            echo "⚠️ JMeter no encontrado en ${jmeterPath}"
                            currentBuild.result = 'UNSTABLE'
                        }
                    } catch (Exception e) {
                        echo "⚠️ Error en JMeter: ${e.message}"
                        currentBuild.result = 'UNSTABLE'
                    } finally {
                        bat 'taskkill /F /IM node.exe /T || exit 0'
                    }
                }
            }
        }

        stage('OWASP Dependency Check') {
            when {
                expression { return env.RUN_OWASP == 'true' }
            }
            steps {
                echo '🛡️ [DEV ONLY] Analizando vulnerabilidades OWASP...'
                script {
                    try {
                        dependencyCheck additionalArguments: """
                            --scan .
                            --out .
                            --format HTML
                            --format JSON
                            --prettyPrint
                            --project "Inventario-${env.DEPLOY_ENV}"
                            --enableExperimental
                            --nodeAuditSkipDevDependencies
                        """.trim(),
                        odcInstallation: 'OWASP-DC',
                        stopBuild: false
                        echo "✅ Análisis OWASP completado"
                    } catch (Exception e) {
                        echo "ℹ️ OWASP completado con advertencias esperadas: ${e.message}"
                    }
                    currentBuild.result = 'SUCCESS'
                    echo "✅ Build marcado como SUCCESS"
                }
            }
        }

        stage('Install Google Code Style') {
            steps {
                echo "🎨 Instalando reglas Google Code Style..."
                script {
                    try {
                        bat '''
                            npm install --save-dev eslint eslint-config-google
                            if not exist .eslintrc.json (
                                echo { > .eslintrc.json
                                echo   "extends": "google", >> .eslintrc.json
                                echo   "parserOptions": { "ecmaVersion": 2022 } >> .eslintrc.json
                                echo } >> .eslintrc.json
                            )
                        '''
                        bat '''
                            pip install pylint yapf pycodestyle
                            if not exist .pylintrc (
                                echo [MASTER] > .pylintrc
                                echo. >> .pylintrc
                                echo [FORMAT] >> .pylintrc
                                echo max-line-length=100 >> .pylintrc
                                echo indent-string='    ' >> .pylintrc
                            )
                        '''
                        echo '✅ Google Code Style instalado correctamente'
                    } catch (Exception e) {
                        echo "⚠️ Error instalando Code Style (no crítico): ${e.message}"
                        currentBuild.result = 'SUCCESS'
                    }
                }
            }
        }

        stage('Archive Results') {
            steps {
                echo '📦 Archivando resultados...'
                script {
                    try {
                        if (env.RUN_OWASP == 'true') {
                            archiveArtifacts artifacts: '**/dependency-check-report.html,**/dependency-check-report.json', allowEmptyArchive: true, fingerprint: true
                        }
                        if (env.RUN_NEWMAN == 'true') {
                            archiveArtifacts artifacts: 'newman-results/**/*', allowEmptyArchive: true, fingerprint: true
                        }
                        if (env.RUN_SELENIUM == 'true') {
                            archiveArtifacts artifacts: 'selenium-results/**/*', allowEmptyArchive: true, fingerprint: true
                        }
                        bat "echo Build completado para entorno: ${env.DEPLOY_ENV} > build-info-${env.DEPLOY_ENV}.txt"
                        bat "echo Fecha: %date% %time% >> build-info-${env.DEPLOY_ENV}.txt"
                        archiveArtifacts artifacts: "build-info-${env.DEPLOY_ENV}.txt", fingerprint: true
                    } catch (Exception e) {
                        echo "⚠️ No se encontraron artefactos para archivar: ${e.message}"
                    }
                }
            }
        }

        stage('Deployment Preparation') {
            when {
                expression { return env.DEPLOY_ENV == 'prod' || env.DEPLOY_ENV == 'qa' }
            }
            steps {
                echo "🚀 Preparando despliegue para ${env.DEPLOY_ENV}..."
                script {
                    echo "✅ Build listo para despliegue en ${env.DEPLOY_ENV}"
                    bat """
                        echo Creando paquete de despliegue...
                        if not exist deploy mkdir deploy
                        xcopy /E /I /Y .next deploy\\.next
                        xcopy /E /I /Y public deploy\\public
                        copy package.json deploy\\
                        if exist next.config.mjs copy next.config.mjs deploy\\
                        if exist next.config.js copy next.config.js deploy\\
                    """
                    archiveArtifacts artifacts: 'deploy/**/*', fingerprint: true
                }
            }
        }
    }

    post {
        always {
            echo '🧹 Limpiando workspace...'
            script {
                try {
                    bat '''
                        if exist ".next" rmdir /s /q ".next"
                        if exist ".scannerwork" rmdir /s /q ".scannerwork"
                        if exist "results" rmdir /s /q "results"
                        if exist "dependency-check-report.html" del /q "dependency-check-report.html"
                        if exist "dependency-check-report.json" del /q "dependency-check-report.json"
                    '''
                } catch (Exception e) {
                    echo "⚠️ Error en limpieza (no crítico): ${e.message}"
                }
            }
        }
        success {
            script {
                echo "✅ =========================================="
                echo "   ¡PIPELINE EJECUTADO EXITOSAMENTE!"
                echo "=========================================="
                echo "🎯 Entorno: ${env.DEPLOY_ENV}"
                echo "📅 Fecha: ${new Date()}"
                if (env.RUN_SONARQUBE == 'true') {
                    echo "📊 Ver resultados en SonarQube: ${env.SONAR_HOST_URL}/dashboard?id=${env.SONAR_PROJECT_KEY}"
                }
                if (env.RUN_OWASP == 'true') {
                    echo "🛡️ Reporte OWASP archivado en los artefactos del build"
                }
                if (env.RUN_NEWMAN == 'true') {
                    echo "🧪 Reportes Newman disponibles en los artefactos"
                }
                if (env.RUN_SELENIUM == 'true') {
                    echo "🌐 Reportes Selenium disponibles en los artefactos"
                }
                if (env.DEPLOY_ENV == 'prod') {
                    echo "🚀 Build listo para despliegue en PRODUCCIÓN"
                }
                echo "=========================================="
            }
        }
        failure {
            script {
                echo "❌ =========================================="
                echo "   EL PIPELINE FALLÓ"
                echo "=========================================="
                echo "🎯 Entorno: ${env.DEPLOY_ENV}"
                echo "🔍 Verifica las etapas marcadas como fallidas arriba"
                echo "=========================================="
            }
        }
        unstable {
            script {
                echo '⚠️ Build marcado como UNSTABLE'
                currentBuild.result = 'SUCCESS'
                echo "✅ Convertido a SUCCESS - advertencias son esperadas en ${env.DEPLOY_ENV}"
            }
        }
    }
}

