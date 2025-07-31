# 🚀 Swing Sage Production Deployment Guide

This guide will walk you through deploying Swing Sage to production using Docker Compose with enterprise-grade features.

## 📋 Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+ recommended) or Windows with WSL2
- **RAM**: Minimum 8GB, recommended 16GB+
- **Storage**: Minimum 50GB free space
- **CPU**: 4+ cores recommended
- **Network**: Stable internet connection

### Software Requirements

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git**: For cloning the repository

### Install Docker (if not installed)

**Ubuntu/Debian:**

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Windows:**
Download and install Docker Desktop from https://www.docker.com/products/docker-desktop

## 🛠️ Quick Start (Automated Deployment)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd swing-sage-final

# Make deployment script executable (Linux/Mac)
chmod +x deploy.sh
```

### 2. Configure Environment

```bash
# Copy environment template
cp env.production.example .env

# Edit the .env file with your production values
nano .env
```

**Required Environment Variables:**

```bash
# Database
DB_PASSWORD=your_secure_database_password_here

# AWS S3 (for video storage and backups)
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
S3_BUCKET=your-swing-sage-production-bucket
S3_BACKUP_BUCKET=your-swing-sage-backup-bucket

# Security
SECRET_KEY=your_super_secret_flask_key_here_make_it_long_and_random
SSL_EMAIL=admin@yourdomain.com
DOMAIN_NAME=yourdomain.com

# Monitoring
GRAFANA_PASSWORD=your_secure_grafana_password
SENTRY_DSN=https://your_sentry_dsn_here

# AI Services
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run Automated Deployment

```bash
# Run the deployment script
./deploy.sh
```

The script will:

- ✅ Check prerequisites
- ✅ Validate environment configuration
- ✅ Create necessary directories
- ✅ Build Docker images
- ✅ Start all services
- ✅ Wait for health checks
- ✅ Show deployment status

## 🔧 Manual Deployment Steps

If you prefer manual deployment or need to troubleshoot:

### 1. Create Directories

```bash
mkdir -p nginx/ssl
mkdir -p nginx/certbot-webroot
mkdir -p monitoring/prometheus
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources
mkdir -p monitoring/logstash/pipeline
mkdir -p monitoring/logstash/config
mkdir -p backup
mkdir -p db
```

### 2. Configure Environment

```bash
cp env.production.example .env
# Edit .env with your values
```

### 3. Build Images

```bash
docker-compose -f docker-compose.production.yml build
```

### 4. Start Services

```bash
docker-compose -f docker-compose.production.yml up -d
```

### 5. Check Status

```bash
docker-compose -f docker-compose.production.yml ps
```

## 🌐 Domain and SSL Setup

### 1. Configure DNS

Point your domain to your server's IP address:

```
A Record: yourdomain.com → YOUR_SERVER_IP
A Record: www.yourdomain.com → YOUR_SERVER_IP
```

### 2. Update Nginx Configuration

Edit `nginx/nginx.conf` and replace `swing-sage.com` with your domain:

```nginx
ssl_certificate /etc/nginx/ssl/live/yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/nginx/ssl/live/yourdomain.com/privkey.pem;
```

### 3. Generate SSL Certificates

```bash
# Start nginx first
docker-compose -f docker-compose.production.yml up -d nginx

# Generate SSL certificate
docker-compose -f docker-compose.production.yml run certbot

# Restart nginx to load certificates
docker-compose -f docker-compose.production.yml restart nginx
```

## 📊 Monitoring Setup

### Grafana Dashboard

1. Access Grafana: `http://YOUR_SERVER_IP:3000`
2. Login: `admin` / `your_grafana_password`
3. Add Prometheus data source: `http://prometheus:9090`
4. Import Swing Sage dashboards

### Prometheus Metrics

- Access: `http://YOUR_SERVER_IP:9090`
- View application metrics and system performance

### Kibana Logs

1. Access Kibana: `http://YOUR_SERVER_IP:5601`
2. Create index patterns for log analysis
3. Set up log dashboards and alerts

## 🔍 Troubleshooting

### Check Service Status

```bash
# View all containers
docker-compose -f docker-compose.production.yml ps

# Check logs
docker-compose -f docker-compose.production.yml logs -f

# Check specific service logs
docker-compose -f docker-compose.production.yml logs -f app
```

### Common Issues

**1. Port Already in Use**

```bash
# Check what's using the port
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# Stop conflicting services
sudo systemctl stop apache2 nginx
```

**2. Database Connection Issues**

```bash
# Check PostgreSQL logs
docker-compose -f docker-compose.production.yml logs postgres

# Test database connection
docker-compose -f docker-compose.production.yml exec postgres psql -U swing_sage -d swing_sage_prod
```

**3. SSL Certificate Issues**

```bash
# Check certificate status
docker-compose -f docker-compose.production.yml run certbot certificates

# Renew certificates
docker-compose -f docker-compose.production.yml run certbot renew
```

**4. Memory Issues**

```bash
# Check system resources
docker stats

# Increase Docker memory limit in Docker Desktop settings
```

### Health Checks

```bash
# Application health
curl -f https://yourdomain.com/health

# Database health
docker-compose -f docker-compose.production.yml exec postgres pg_isready -U swing_sage

# Redis health
docker-compose -f docker-compose.production.yml exec redis redis-cli ping
```

## 📈 Scaling and Performance

### Horizontal Scaling

```bash
# Scale app instances
docker-compose -f docker-compose.production.yml up -d --scale app=5

# Scale workers
docker-compose -f docker-compose.production.yml up -d --scale video_worker=3
```

### Resource Monitoring

```bash
# Monitor resource usage
docker stats

# Check disk usage
df -h

# Monitor logs
docker-compose -f docker-compose.production.yml logs -f --tail=100
```

## 🔄 Backup and Recovery

### Manual Backup

```bash
# Database backup
docker-compose -f docker-compose.production.yml exec postgres pg_dump -U swing_sage swing_sage_prod > backup.sql

# Redis backup
docker-compose -f docker-compose.production.yml exec redis redis-cli BGSAVE
```

### Automated Backups

Backups are automatically scheduled via the backup service. Check logs:

```bash
docker-compose -f docker-compose.production.yml logs backup
```

## 🛡️ Security Considerations

### Firewall Setup

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Regular Updates

```bash
# Update Docker images
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d

# Update system packages
sudo apt update && sudo apt upgrade -y
```

## 📞 Support and Maintenance

### Daily Operations

```bash
# Check service status
docker-compose -f docker-compose.production.yml ps

# View recent logs
docker-compose -f docker-compose.production.yml logs --tail=50

# Monitor resource usage
docker stats --no-stream
```

### Weekly Maintenance

```bash
# Update SSL certificates
docker-compose -f docker-compose.production.yml run certbot renew

# Clean up old images
docker image prune -f

# Check disk space
df -h
```

### Monthly Tasks

```bash
# Review logs for issues
docker-compose -f docker-compose.production.yml logs --since="30d" | grep ERROR

# Update application
git pull
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d

# Review monitoring dashboards
# Check Grafana and Kibana for trends
```

## 🎯 Production Checklist

Before going live, ensure:

- [ ] All environment variables are set correctly
- [ ] SSL certificates are valid and working
- [ ] Domain DNS is pointing to the server
- [ ] Monitoring dashboards are configured
- [ ] Backup system is working
- [ ] Firewall rules are in place
- [ ] System resources are adequate
- [ ] Application health checks are passing
- [ ] Error logging is configured
- [ ] Performance monitoring is active

## 🚀 Success!

Your Swing Sage production deployment is now ready!

**Access URLs:**

- 🌐 Main Application: `https://yourdomain.com`
- 📊 Grafana Dashboard: `http://YOUR_SERVER_IP:3000`
- 📈 Prometheus Metrics: `http://YOUR_SERVER_IP:9090`
- 📋 Kibana Logs: `http://YOUR_SERVER_IP:5601`

**Next Steps:**

1. Test the application thoroughly
2. Configure monitoring alerts
3. Set up automated backups
4. Document your deployment
5. Train your team on monitoring tools

Happy golfing! ⛳️🏌️‍♂️
