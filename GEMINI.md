# 🤖 GEMINI CLI - PROJECT CONTEXT
## "Proyecto Semilla - Vibecoding-Native SaaS Platform"

**Project**: Proyecto Semilla  
**Type**: Open Source SaaS Multi-tenant Platform  
**Vision**: Democratize enterprise development through AI-assisted coding  

---

## 🎯 **PROJECT OVERVIEW**

**Proyecto Semilla** is the first Vibecoding-native platform designed to make enterprise development accessible through conversational AI assistance.

### **Core Mission**
Enable developers to build complex enterprise modules through natural language conversations with AI, following established architectural patterns and best practices.

---

## 🏗️ **TECHNICAL STACK**

### **Backend**
- **Framework**: FastAPI + SQLAlchemy
- **Database**: PostgreSQL 15+ with Row-Level Security
- **Architecture**: Multi-tenant SaaS design
- **Security**: JWT authentication + comprehensive audit logging
- **APIs**: RESTful design with OpenAPI documentation

### **Frontend**
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **Design**: Responsive and mobile-optimized

### **Infrastructure**
- **Containerization**: Docker + Docker Compose
- **Development**: Hot reload and development-optimized
- **Testing**: Comprehensive test framework
- **Documentation**: Auto-generated API docs

---

## 🚀 **KEY FEATURES**

### **Multi-Tenancy**
- Complete tenant isolation
- Scalable architecture
- Per-tenant customization capabilities

### **Modern Development Stack**
- Fast development cycles
- Type-safe development
- Modern UI components
- Performance optimized

### **AI Integration Ready**
- Model Context Protocol (MCP) support
- Structured for AI-assisted development
- Extensible architecture for AI tools

---

## 🔧 **DEVELOPMENT SETUP**

### **Quick Start**
```bash
# Clone the repository
git clone https://github.com/untalcamilomedina/proyecto-semilla.git
cd proyecto-semilla

# Start all services
docker-compose up -d

# Verify system health
./scripts/daily-check.sh
```

### **Service Endpoints**
- **Backend API**: http://localhost:7777
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:7777/docs

### **Development Workflow**
```bash
# Before making changes
./scripts/daily-check.sh

# After making changes
git add .
git commit -m "descriptive message"
./scripts/daily-check.sh
```

---

## 📚 **DOCUMENTATION**

- **README**: Complete project overview and setup instructions
- **API Docs**: Auto-generated OpenAPI documentation at `/docs`
- **CHANGELOG**: Version history and feature updates
- **CONTRIBUTING**: Guidelines for contributing to the project

---

## 🤝 **CONTRIBUTING**

This is an open-source project welcoming contributions from the community. Please review our contributing guidelines and feel free to submit issues, feature requests, or pull requests.

### **Development Standards**
- Follow existing code patterns and conventions
- Ensure all tests pass before submitting PRs
- Maintain comprehensive documentation
- Follow semantic versioning for releases

---

## 🌟 **VISION & GOALS**

**Proyecto Semilla** aims to bridge the gap between complex enterprise development needs and accessible, AI-assisted development workflows. By providing a solid, well-documented foundation, developers can build sophisticated applications while leveraging AI assistance for rapid development cycles.

---

*This project represents the intersection of modern development practices, enterprise-grade architecture, and AI-assisted development workflows.*