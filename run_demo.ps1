Write-Host "🚀 Construyendo imagen Docker..."
docker stop resqfood_app 2>$null
docker rm resqfood_app 2>$null
docker build -t resqfood:latest .

Write-Host "🚀 Levantando contenedor..."
docker run --env-file .env -p 8000:8000 --name resqfood_app -d resqfood:latest

Start-Sleep -Seconds 3

Write-Host "🌍 Iniciando ngrok..."
Start-Process powershell -ArgumentList "ngrok http 8000"

Write-Host "✨ Todo listo!"
Write-Host "➜ Django: http://127.0.0.1:8000"
Write-Host "➜ ngrok: abrirá una segunda ventana con tu URL pública"
    