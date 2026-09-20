import streamlit as st
import json
from datetime import datetime
from calendar import monthrange
import os

# ================= CONFIGURAÇÕES =================
st.set_page_config(
    page_title="Agenda Médica — Prefeitura de Jacareí",
    page_icon="🏛️",
    layout="centered"
)

# CSS igual antes...
st.markdown("""
<style>
.stApp {
    background-image: url('fundo_jacarei.jpg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
div.block-container {
    background-color: rgba(255, 255, 255, 0.92);
    padding: 2rem 3rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    max-width: 900px;
    margin-top: 2rem;
    margin-bottom: 2rem;
}
h1, h2, h3, h4 { color: #003366; text-align: center; }
button[kind="primary"] { background-color: #0052CC !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ================= DADOS — VERSÃO CORRIGIDA ✅ =================
ARQUIVO_DADOS = "dados_agenda_web.json"
ARQUIVO_BACKUP = "backup_dados.json"

TODOS_HORARIOS = [
    "08:00", "08:15", "08:30", "08:45",
    "09:00", "09:15", "09:30", "09:45",
    "10:00", "10:15", "10:30", "10:45",
    "11:00", "11:15", "11:30", "11:45",
    "13:00", "13:15", "13:30", "13:45",
    "14:00", "14:15", "14:30", "14:45",
    "15:00", "15:15", "15:30", "15:45",
    "16:00", "16:15", "16:20"
]
TOTAL_HORARIOS = len(TODOS_HORARIOS)

def carregar_dados():
    # Tenta carregar o arquivo principal
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # Tenta carregar o backup
    if os.path.exists(ARQUIVO_BACKUP):
        try:
            with open(ARQUIVO_BACKUP, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # Retorna padrão se nada existir
    return {"medicos": [{"nome":"Paulo"},{"nome":"Andrea"},{"nome":"Felipe"}], "agendamentos": []}

def salvar_dados(dados):
    # Salva no arquivo principal
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    # Cria também um backup de segurança
    with open(ARQUIVO_BACKUP, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ================= CABEÇALHO =================
def cabecalho():
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem;">
        <h2 style="color: #003366; margin-bottom: 0;">🏛️ Prefeitura de Jacareí</h2>
        <h4 style="color: #444444; margin-top: 0;">Secretaria de Saúde — Agendamento Médico</h4>
        <hr style="border: 1px solid #0052CC; margin: 1rem 0;">
    </div>
    """, unsafe_allow_html=True)

# ================= LOGIN =================
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.eh_leitura = False

if not st.session_state.logado:
    cabecalho()
    st.markdown("<h3 style='text-align: center;'>🔐 Acesso ao Sistema</h3>", unsafe_allow_html=True)
    col_esq, col_meio, col_dir = st.columns([1, 2, 1])
    with col_meio:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("ENTRAR", type="primary", use_container_width=True):
            if usuario == "admin" and senha == "admin123":
                st.session_state.logado = True
                st.session_state.eh_leitura = False
                st.rerun()
            elif usuario == "colaborador123" and senha == "colaborador123":
                st.session_state.logado = True
                st.session_state.eh_leitura = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")
    st.stop()

# ================= SISTEMA PRINCIPAL =================
dados = carregar_dados()
cabecalho()

if st.session_state.eh_leitura:
    st.info("👁️ **MODO VISUALIZAÇÃO** — Apenas consulta")
else:
    st.success("🔑 **MODO ADMINISTRADOR** — Pode cadastrar e agendar")

if st.button("🚪 Sair"):
    st.session_state.logado = False
    st.rerun()

# Navegação mês
if "mes_atual" not in st.session_state:
    st.session_state.mes_atual = datetime.now().month
    st.session_state.ano_atual = datetime.now().year

col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if st.button("◀ Mês"):
        st.session_state.mes_atual -= 1
        if st.session_state.mes_atual < 1:
            st.session_state.mes_atual = 12
            st.session_state.ano_atual -= 1
with col2:
    meses = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
             "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    st.markdown(f"<h3 style='text-align: center;'>{meses[st.session_state.mes_atual-1]} {st.session_state.ano_atual}</h3>", unsafe_allow_html=True)
with col3:
    if st.button("Mês ▶"):
        st.session_state.mes_atual += 1
        if st.session_state.mes_atual > 12:
            st.session_state.mes_atual = 1
            st.session_state.ano_atual += 1

# Selecionar médico
col_esq, col_meio, col_dir = st.columns([1, 2, 1])
with col_meio:
    medico_nome = st.selectbox("👨‍⚕️ Selecione o Médico", [m["nome"] for m in dados["medicos"]])

# Cadastrar médico
if not st.session_state.eh_leitura:
    with st.expander("➕ Cadastrar Novo Médico"):
        col_e, col_m, col_d = st.columns([1, 2, 1])
        with col_m:
            novo_nome = st.text_input("Nome Completo do Médico")
            if st.button("✅ Salvar Médico") and novo_nome:
                dados["medicos"].append({"nome": novo_nome})
                salvar_dados(dados)
                st.success(f"Médico **{novo_nome}** cadastrado com sucesso!")
                st.rerun()

# Calendário — CORRIGIDO ✅
st.markdown("<h4 style='text-align: center; margin-top: 1rem;'>📅 Calendário de Atendimentos</h4>", unsafe_allow_html=True)
primeiro_dia, total_dias = monthrange(st.session_state.ano_atual, st.session_state.mes_atual)
dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
cols = st.columns(5)
for i, d in enumerate(dias_semana):
    cols[i].markdown(f"<p style='text-align: center; font-weight: bold; color: #003366;'>{d}</p>", unsafe_allow_html=True)

coluna = primeiro_dia
if coluna >= 5:
    coluna = 0

for dia in range(1, total_dias + 1):
    dia_semana = datetime(st.session_state.ano_atual, st.session_state.mes_atual, dia).weekday()
    if dia_semana >= 5:
        coluna = 0
        continue
    
    data_str = f"{st.session_state.ano_atual}-{st.session_state.mes_atual:02d}-{dia:02d}"
    qtd = len([a for a in dados["agendamentos"]
               if a["medico"] == medico_nome and a["data"] == data_str])
    
    if qtd == TOTAL_HORARIOS: cor = "🟠"
    elif qtd > 0: cor = "🟡"
    else: cor = "🟢"
    
    with cols[coluna]:
        if st.button(f"{cor} {dia}", key=f"dia_{dia}", use_container_width=True):
            st.session_state.dia_selecionado = dia
            st.session_state.data_selecionada = data_str
    coluna += 1
    if coluna > 4: coluna = 0

# Horários do dia selecionado
if "dia_selecionado" in st.session_state:
    dia_sel = st.session_state.dia_selecionado
    data_sel = st.session_state.data_selecionada
    st.markdown(f"<h4 style='text-align: center; margin-top: 1rem;'>⏰ Horários — {dia_sel:02d}/{st.session_state.mes_atual:02d}/{st.session_state.ano_atual}</h4>", unsafe_allow_html=True)
    
    agendamentos_dia = [a for a in dados["agendamentos"]
                        if a["medico"] == medico_nome and a["data"] == data_sel]
    
    opcoes_solicitacao = [
        "Sem CID", "Sem Carimbo", "Atestado mais de 6 dias",
        "Atestado acima de 48 horas", "MEMO", "Exame",
        "Atestado Ilegível", "Probatório", "Periódico",
        "Atestado por Período", "Artigo 112", "Maternidade",
        "Atestado (sem erros)"
    ]
    opcoes_status = ["AGENDADO", "COMPARECEU", "FALTA", "DESMARCADO"]
    
    for hora in TODOS_HORARIOS:
        ag = next((a for a in agendamentos_dia if a["hora"] == hora), None)
        
        if ag:
            st.markdown(f"**{hora}** — {ag['nome_servidor']} | {ag['status']}")
            if not st.session_state.eh_leitura:
                with st.expander(f"✏️ Editar — {hora}"):
                    with st.form(f"form_{hora}"):
                        nome = st.text_input("Nome do Servidor", value=ag.get("nome_servidor", ""))
                        matricula = st.text_input("Matrícula", value=ag.get("matricula", ""))
                        tipo_atend = st.text_input("Tipo de Atendimento", value=ag.get("tipo_atendimento", ""))
                        tipo_solic = st.selectbox("Tipo de Solicitação", opcoes_solicitacao, 
                            index=opcoes_solicitacao.index(ag.get("tipo_solicitacao", opcoes_solicitacao[0])) 
                            if ag.get("tipo_solicitacao") in opcoes_solicitacao else 0)
                        status = st.selectbox("Status", opcoes_status,
                            index=opcoes_status.index(ag.get("status", "AGENDADO")))
                        obs = st.text_area("Observação", value=ag.get("observacao", ""))
                        
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.form_submit_button("💾 Salvar"):
                                idx = dados["agendamentos"].index(ag)
                                dados["agendamentos"][idx] = {
                                    "medico": medico_nome, "data": data_sel, "hora": hora,
                                    "nome_servidor": nome, "matricula": matricula,
                                    "tipo_atendimento": tipo_atend, "tipo_solicitacao": tipo_solic,
                                    "observacao": obs, "status": status
                                }
                                salvar_dados(dados)
                                st.success("✅ Salvo com sucesso!")
                                st.rerun()
                        with col_b2:
                            if st.form_submit_button("🗑️ Excluir"):
                                dados["agendamentos"].remove(ag)
                                salvar_dados(dados)
                                st.success("✅ Excluído!")
                                st.rerun()
        else:
            st.markdown(f"⚪ **{hora}** — Disponível")
            if not st.session_state.eh_leitura:
                with st.expander(f"📝 Agendar — {hora}"):
                    with st.form(f"form_novo_{hora}"):
                        nome = st.text_input("Nome do Servidor")
                        matricula = st.text_input("Matrícula")
                        tipo_atend = st.text_input("Tipo de Atendimento")
                        tipo_solic = st.selectbox("Tipo de Solicitação", opcoes_solicitacao)
                        status = st.selectbox("Status", opcoes_status, index=0)
                        obs = st.text_area("Observação")
                        
                        if st.form_submit_button("✅ Confirmar Agendamento"):
                            if nome and matricula:
                                dados["agendamentos"].append({
                                    "medico": medico_nome, "data": data_sel, "hora": hora,
                                    "nome_servidor": nome, "matricula": matricula,
                                    "tipo_atendimento": tipo_atend, "tipo_solicitacao": tipo_solic,
                                    "observacao": obs, "status": status
                                })
                                salvar_dados(dados)
                                st.success("✅ Agendado com sucesso!")
                                st.rerun()
                            else:
                                st.warning("⚠️ Preencha Nome e Matrícula!")
    
    if st.button("❌ Fechar Dia"):
        del st.session_state.dia_selecionado
        del st.session_state.data_selecionada
        st.rerun()

# Rodapé
st.markdown("""
<hr style="border: 1px solid #e0e0e0; margin-top: 2rem;">
<p style="text-align: center; color: #888888; font-size: 0.85rem;">
Prefeitura de Jacareí — Sistema de Agendamento Médico<br>
Última atualização: {}
</p>
""".format(datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)