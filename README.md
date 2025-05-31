
# 🚀 Dynamic Dock

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
