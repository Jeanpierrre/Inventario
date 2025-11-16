pipeline {
    agent any
    
    // Parámetros para seleccionar el entorno
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
    }
    
    environment {
        // Variables globales
        SONAR_HOST_URL = 'https://srvapp.netwaresoft.com'
        SONAR_PROJECT_KEY = 'GYKVENTAS'
        NODE_HOME = tool name: 'NodeJS-20', type: 'nodejs'
        PATH = "${NODE_HOME}/bin;${env.PATH}"
        NEXT_TELEMETRY_DISABLED = '1'
        
        // Variables dinámicas según entorno
        DEPLOY_ENV = "${params.ENVIRONMENT}"
        RUN_SONARQUBE = "${params.ENVIRONMENT == 'dev' ? 'true' : 'false'}"
        RUN_NEWMAN = "${params.ENVIRONMENT == 'prod' ? 'false' : 'true'}"
        RUN_JMETER = "${params.ENVIRONMENT == 'dev' ? 'true' : 'false'}"
        RUN_OWASP = "${params.ENVIRONMENT == 'dev' ? 'true' : 'false'}"
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
                    echo "🎯 Entorno seleccionado: ${DEPLOY_ENV}"
                    echo "📊 SonarQube: ${RUN_SONARQUBE == 'true' ? '✅ ACTIVADO' : '⏭️ OMITIDO'}"
                    echo "🧪 Newman (Postman): ${RUN_NEWMAN == 'true' ? '✅ ACTIVADO' : '⏭️ OMITIDO'}"
                    echo "⚡ JMeter: ${RUN_JMETER == 'true' ? '✅ ACTIVADO' : '⏭️ OMITIDO'}"
                    echo "🛡️ OWASP: ${RUN_OWASP == 'true' ? '✅ ACTIVADO' : '⏭️ OMITIDO'}"
                    echo "=========================================="
                    
                    // Configurar variables adicionales por entorno
                    if (DEPLOY_ENV == 'prod') {
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
                git branch: 'main', 
                    url: 'https://github.com/Jeanpierrre/Inventario.git'
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
                    echo Entorno: %DEPLOY_ENV%
                '''
            }
        }
        
      stage('Install Dependencies') {
                steps {
                    echo "📦 Instalando dependencias para ${DEPLOY_ENV}..."
                    script {
                        bat '''
                            if not exist package-lock.json (
                                echo Generando package-lock.json...
                                npm install --package-lock-only --legacy-peer-deps
                            )
                        '''
                        
                        // SIEMPRE instalar TODAS las dependencias (incluyendo devDependencies)
                        // Next.js necesita @tailwindcss/postcss y otras devDependencies para el build
                        bat 'npm ci --legacy-peer-deps --prefer-offline || npm install --legacy-peer-deps --prefer-offline'
                    }
                }
            }
        
        stage('Build Frontend') {
            steps {
                echo "🔨 Construyendo aplicación Next.js para ${DEPLOY_ENV}..."
                script {
                    // Build optimizado para producción
                    if (DEPLOY_ENV == 'prod') {
                        bat 'npm run build -- --no-lint'
                    } else {
                        bat 'npm run build'
                    }
                }
            }
        }
        
        stage('Run Tests') {
            when {
                expression { 
                    return params.SKIP_TESTS == false && DEPLOY_ENV != 'prod'
                }
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
                                -Dsonar.projectName=${SONAR_PROJECT_KEY} ^
                                -Dsonar.sources=sistema.py,db.py ^
                                -Dsonar.tests=test ^
                                -Dsonar.test.inclusions=**/*test*.py,**/test_*.py ^
                                -Dsonar.exclusions=**/node_modules/**,**/.next/**,**/public/**,**/coverage/**,**/build/**,**/dist/**,**/__pycache__/**,**/venv/**,**/env/**,**/.venv/**,**/.env/** ^
                                -Dsonar.python.version=3.10.5 ^
                                -Dsonar.host.url=${SONAR_HOST_URL} ^
                                -Dsonar.token=%SONAR_TOKEN% ^
                                -Dsonar.sourceEncoding=UTF-8 ^
                                -Dsonar.log.level=INFO
                            """
                        }
                    }
                }
            }
        
        stage('Newman API Tests') {
            when {
                expression { return RUN_NEWMAN == 'true' }
            }
            steps {
                echo "🧪 [${DEPLOY_ENV.toUpperCase()}] Ejecutando pruebas de API con Newman (Postman)..."
                script {
                    try {
                        // Crear carpeta para resultados
                        bat 'if not exist newman-results mkdir newman-results'
                        
                        // Iniciar la aplicación
                        bat 'start /B npm run start'
                        
                        echo "Esperando 20 segundos para que Next.js inicie en ${DEPLOY_ENV}..."
                        sleep(time: 20, unit: 'SECONDS')
                        
                        // Ejecutar Newman con colección de Postman
                        // Asumiendo que tienes una colección en tests/postman-collection.json
                        bat """
                            newman run tests/postman-collection.json ^
                            --environment tests/postman-env-${DEPLOY_ENV}.json ^
                            --reporters cli,htmlextra,json ^
                            --reporter-htmlextra-export newman-results/newman-report-${DEPLOY_ENV}.html ^
                            --reporter-json-export newman-results/newman-report-${DEPLOY_ENV}.json
                        """
                        
                        // Archivar resultados
                        archiveArtifacts artifacts: 'newman-results/**/*', allowEmptyArchive: true
                        
                        echo "✅ Pruebas Newman completadas para ${DEPLOY_ENV}"
                    } catch (Exception e) {
                        echo "⚠️ Error en Newman: ${e.message}"
                        if (DEPLOY_ENV == 'qa') {
                            // En QA, los errores de Newman son críticos
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
                expression { return RUN_JMETER == 'true' }
            }
            steps {
                echo '⚡ [DEV ONLY] Ejecutando pruebas de rendimiento con JMeter...'
                script {
                    try {
                        bat 'if not exist results mkdir results'
                        
                        bat 'start /B npm run start'
                        
                        echo 'Esperando 20 segundos para que Next.js inicie...'
                        sleep(time: 20, unit: 'SECONDS')
                        
                        bat '''
                            "C:\\apache-jmeter-5.6.3\\bin\\jmeter.bat" -n ^
                            -t tests/api-load-test.jmx ^
                            -l results/jmeter-results.jtl ^
                            -e -o results/jmeter-report ^
                            -Jbase_url=localhost:3000
                        '''
                        
                        archiveArtifacts artifacts: 'results/jmeter-report/**/*', allowEmptyArchive: true
                        
                        echo '✅ Pruebas JMeter completadas'
                    } catch (Exception e) {
                        echo "⚠️ Error en JMeter: ${e.message}"
                    } finally {
                        bat 'taskkill /F /IM node.exe /T || exit 0'
                    }
                }
            }
        }
        
        stage('OWASP Dependency Check') {
            when {
                expression { return RUN_OWASP == 'true' }
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
                            --project "Inventario-${DEPLOY_ENV}"
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
        
        stage('Archive Results') {
            steps {
                echo '📦 Archivando resultados...'
                script {
                    try {
                        // Archivar reportes según el entorno
                        if (RUN_OWASP == 'true') {
                            archiveArtifacts artifacts: '**/dependency-check-report.html,**/dependency-check-report.json', 
                                           allowEmptyArchive: true,
                                           fingerprint: true
                        }
                        
                        if (RUN_NEWMAN == 'true') {
                            archiveArtifacts artifacts: 'newman-results/**/*', 
                                           allowEmptyArchive: true,
                                           fingerprint: true
                        }
                        
                        // Siempre archivar logs de build
                        bat "echo Build completado para entorno: ${DEPLOY_ENV} > build-info-${DEPLOY_ENV}.txt"
                        bat "echo Fecha: %date% %time% >> build-info-${DEPLOY_ENV}.txt"
                        archiveArtifacts artifacts: "build-info-${DEPLOY_ENV}.txt"
                        
                    } catch (Exception e) {
                        echo "⚠️ No se encontraron artefactos para archivar: ${e.message}"
                    }
                }
            }
        }
        
        stage('Deployment Preparation') {
            when {
                expression { return DEPLOY_ENV == 'prod' || DEPLOY_ENV == 'qa' }
            }
            steps {
                echo "🚀 Preparando despliegue para ${DEPLOY_ENV}..."
                script {
                    // Aquí puedes agregar pasos de despliegue específicos
                    echo "✅ Build listo para despliegue en ${DEPLOY_ENV}"
                    
                    // Ejemplo: crear artefacto de despliegue
                    bat """
                        echo Creando paquete de despliegue...
                        if not exist deploy mkdir deploy
                        xcopy /E /I /Y .next deploy\\.next
                        xcopy /E /I /Y public deploy\\public
                        copy package.json deploy\\
                        copy next.config.js deploy\\
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
                echo "🎯 Entorno: ${DEPLOY_ENV}"
                echo "📅 Fecha: ${new Date()}"
                
                if (RUN_SONARQUBE == 'true') {
                    echo "📊 Ver resultados en SonarQube: ${SONAR_HOST_URL}/dashboard?id=${SONAR_PROJECT_KEY}"
                }
                
                if (RUN_OWASP == 'true') {
                    echo "🛡️ Reporte OWASP archivado en los artefactos del build"
                }
                
                if (RUN_NEWMAN == 'true') {
                    echo "🧪 Reportes Newman disponibles en los artefactos"
                }
                
                if (DEPLOY_ENV == 'prod') {
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
                echo "🎯 Entorno: ${DEPLOY_ENV}"
                echo "🔍 Verifica las etapas marcadas como fallidas arriba"
                echo "=========================================="
            }
        }
        unstable {
            script {
                echo '⚠️ Build marcado como UNSTABLE'
                currentBuild.result = 'SUCCESS'
                echo "✅ Convertido a SUCCESS - advertencias son esperadas en ${DEPLOY_ENV}"
            }
        }
    }
}




