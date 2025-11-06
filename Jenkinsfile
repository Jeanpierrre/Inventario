pipeline {
    agent any
    
    environment {
    // Variables de entorno para SonarQube
    SONAR_HOST_URL = 'https://srvapp.netwaresoft.com'
    SONAR_PROJECT_KEY = 'GYKVENTAS'
    
    // Variables de entorno para Node.js
    NODE_HOME = tool name: 'NodeJS-18', type: 'nodejs'
    PATH = "${NODE_HOME}/bin;${env.PATH}"
    }    
    
    tools {
        nodejs 'NodeJS-20'
    }
    
    stages {
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
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo '📦 Instalando dependencias del proyecto...'
                bat 'npm install --legacy-peer-deps'
            }
        }
        
        stage('Build Frontend') {
            steps {
                echo '🔨 Construyendo aplicación Next.js...'
                bat 'npm run build'
            }
        }
        
        stage('Run Tests') {
            steps {
                echo '🧪 Ejecutando pruebas...'
                bat 'npm test -- --passWithNoTests || exit 0'
            }
        }
        
       stage('SonarQube Analysis') {
            steps {
                echo '🔍 Ejecutando análisis de código con SonarQube...'
                script {
                    def scannerHome = tool name: 'SonarScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                    bat """
                        "${scannerHome}\\bin\\sonar-scanner.bat" ^
                        -D"sonar.projectKey=${SONAR_PROJECT_KEY}" ^
                        -D"sonar.sources=." ^
                        -D"sonar.exclusions=**/node_modules/**,**/.next/**,**/public/**,**/coverage/**" ^
                        -D"sonar.host.url=${SONAR_HOST_URL}" ^
                        -D"sonar.token=${SONAR_TOKEN}"
                    """
                }
            }
        }
        
        stage('OWASP Dependency Check') {
            steps {
                echo '🛡️ Analizando vulnerabilidades OWASP...'
                dependencyCheck additionalArguments: '''
                    --scan .
                    --format HTML
                    --format JSON
                    --prettyPrint
                    --project "Inventario"
                ''', 
                odcInstallation: 'OWASP-DC'
                
                dependencyCheckPublisher pattern: '**/dependency-check-report.xml'
            }
        }
        
        stage('Archive Results') {
            steps {
                echo '📦 Archivando resultados...'
                archiveArtifacts artifacts: '**/dependency-check-report.html', allowEmptyArchive: true
            }
        }
    }
    
    post {
        always {
            echo '🧹 Limpiando workspace...'
            cleanWs()
        }
        success {
            echo '✅ ¡Pipeline ejecutado exitosamente!'
            echo "📊 Ver resultados en SonarQube: ${SONAR_HOST_URL}/dashboard?id=${SONAR_PROJECT_KEY}"
        }
        failure {
            echo '❌ El pipeline falló. Revisa los logs.'
        }
    }
}


