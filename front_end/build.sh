echo "Building the app"
npm run build

echo "Delpoying to server"
scp -r build/* /var/www/128.199.153.206

echo "Deployment complete"