# 🚀 Dynamic Dock (English Version)

**Dynamic Dock** is a molecular docking platform that enables protein-ligand docking analysis and molecular dynamics preparation.

---

## 🧬 Features

- 📥 Load PDB structures (via ID or file upload)
- 🔍 Analyze and visualize co-crystallized ligands
- 🎯 Automatically identify the active site
- ⚗️ Perform molecular docking with AutoDock Vina
- 📤 Download results and prepare for molecular dynamics

---

## 📁 Project Structure

```
dynamic_dock/
├── frontend/           # Frontend application (React)
├── backend/            # Backend API (FastAPI)
├── docker/             # Docker configuration
└── README.md           # This file
```

---

## ✅ Prerequisites

- ⚙️ Node.js **16+**
- 🐍 Python **3.8+**
- 🐳 Docker *(optional)*
- 🧪 AutoDock Vina
- 🧬 RDKit
- 🔄 OpenBabel

---

## 🛠️ Getting Started

### 🔙 Backend

1. Go to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies with **Poetry**:
   ```bash
   poetry install
   ```

3. Start the server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

---

### 🔜 Frontend

1. Go to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The application will be available at:  
👉 **http://localhost:3000**

---

## 🚢 Deployment

### 🧠 Backend (FastAPI) – Render

1. Go to [🔗 Render](https://render.com) and create a new **Web Service**.
2. Connect your Git repository with the backend.
3. Configure the following:

   - **Root Directory:** `backend`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Runtime:** Python 3.8+

4. Add environment variables if needed, such as:
   ```env
   CORS_ORIGINS=https://your-frontend.netlify.app
   ```

5. After deployment, the backend will be accessible at:  
   🌐 `https://dynamic-dock-backend.onrender.com`

---

### 🌐 Frontend (React) – Netlify

1. Install the Netlify CLI:
   ```bash
   npm install -g netlify-cli
   ```

2. Log in:
   ```bash
   netlify login
   ```

3. Initialize the project:
   ```bash
   netlify init
   ```

4. Build the project:
   ```bash
   npm run build
   ```

5. Deploy preview:
   ```bash
   netlify deploy
   ```

6. Deploy to production:
   ```bash
   netlify deploy --prod
   ```

> 💡 **Tip:** In the Netlify dashboard, define the environment variable:
>
> ```env
> REACT_APP_BACKEND_URL=https://dynamic-dock-backend.onrender.com
> ```

---

## 📄 License

**MIT License** — feel free to use, modify, and share!

---

# 🚀 Dynamic Dock (portuguese)

**Dynamic Dock** é uma plataforma de *molecular docking* que permite análises de acoplamento proteína-ligante e preparação para simulações de dinâmica molecular.

---

## 🧬 Funcionalidades

- 📥 Carregamento de estruturas PDB (via ID ou upload de arquivo)
- 🔍 Análise e visualização de ligantes co-cristalizados
- 🎯 Identificação automática do sítio ativo
- ⚗️ *Molecular docking* com AutoDock Vina
- 📤 Download dos resultados e preparação para dinâmica molecular

---

## 📁 Estrutura do Projeto

```
dynamic_dock/
├── frontend/           # Aplicação frontend (React)
├── backend/            # API backend (FastAPI)
├── docker/             # Configurações Docker
└── README.md           # Este arquivo
```

---

## ✅ Pré-requisitos

- ⚙️ Node.js **16+**
- 🐍 Python **3.8+**
- 🐳 Docker *(opcional)*
- 🧪 AutoDock Vina
- 🧬 RDKit
- 🔄 OpenBabel

---

## 🛠️ Primeiros Passos

### 🔙 Backend

1. Acesse o diretório do backend:
   ```bash
   cd backend
   ```

2. Instale as dependências com **Poetry**:
   ```bash
   poetry install
   ```

3. Inicie o servidor:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

---

### 🔜 Frontend

1. Acesse o diretório do frontend:
   ```bash
   cd frontend
   ```

2. Instale as dependências:
   ```bash
   npm install
   ```

3. Inicie o servidor de desenvolvimento:
   ```bash
   npm start
   ```

A aplicação estará disponível em:  
👉 **http://localhost:3000**

---

## 🚢 Deploy

### 🧠 Backend (FastAPI) – Render

1. Acesse [🔗 Render](https://render.com) e crie um novo **Web Service**.
2. Conecte seu repositório Git com o backend.
3. Configure os campos:

   - **Root Directory:** `backend`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Runtime:** Python 3.8+

4. Adicione variáveis de ambiente se necessário, como:
   ```env
   CORS_ORIGINS=https://seu-site.netlify.app
   ```

5. Após o deploy, o backend estará disponível, por exemplo, em:  
   🌐 `https://dynamic-dock-backend.onrender.com`

---

### 🌐 Frontend (React) – Netlify

1. Instale o CLI do Netlify:
   ```bash
   npm install -g netlify-cli
   ```

2. Faça login:
   ```bash
   netlify login
   ```

3. Inicialize o projeto:
   ```bash
   netlify init
   ```

4. Compile o projeto:
   ```bash
   npm run build
   ```

5. Deploy de pré-visualização:
   ```bash
   netlify deploy
   ```

6. Deploy para produção:
   ```bash
   netlify deploy --prod
   ```

> 💡 **Dica:** No painel da Netlify, defina a variável de ambiente:
>
> ```env
> REACT_APP_BACKEND_URL=https://dynamic-dock-backend.onrender.com
> ```

---

## 📄 Licença

**MIT License** — sinta-se livre para usar, modificar e compartilhar!

---
