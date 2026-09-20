import streamlit as st
import json
from datetime import datetime
from calendar import monthrange

ARQUIVO_DADOS = "dados_agenda_web.json"

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
    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"medicos": [{"nome":"Paulo"},{"nome":"Andrea"},{"nome":"Felipe"}], "agendamentos": []}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ---- TELA DE LOGIN ----
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.eh_leitura = False

if not st.session_state.logado:
    st.title("🔐 SISTEMA DE AGENDA — LOGIN")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("ENTRAR", type="primary"):
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

# ---- SISTEMA PRINCIPAL ----
dados = carregar_dados()

# Cabeçalho
st.title("📋 AGENDAMENTO MÉDICO")
if st.session_state.eh_leitura:
    st.info("👁️ MODO VISUALIZAÇÃO — Sem permissão para alterar")
else:
    st.success("🔑 MODO ADMINISTRADOR — Pode alterar")

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
    st.subheader(f"{meses[st.session_state.mes_atual-1]} {st.session_state.ano_atual}")
with col3:
    if st.button("Mês ▶"):
        st.session_state.mes_atual += 1
        if st.session_state.mes_atual > 12:
            st.session_state.mes_atual = 1
            st.session_state.ano_atual += 1

# Selecionar médico
medico_nome = st.selectbox("Selecione o Médico", [m["nome"] for m in dados["medicos"]])

# Cadastrar médico (só admin)
if not st.session_state.eh_leitura:
    with st.expander("➕ Cadastrar Novo Médico"):
        novo_nome = st.text_input("Nome do Médico")
        if st.button("Salvar Médico") and novo_nome:
            dados["medicos"].append({"nome": novo_nome})
            salvar_dados(dados)
            st.success(f"Médico {novo_nome} cadastrado!")
            st.rerun()

# Calendário
st.subheader(f"📅 Calendário — {medico_nome}")
primeiro_dia, total_dias = monthrange(st.session_state.ano_atual, st.session_state.mes_atual)

dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex"]
cols = st.columns(5)
for i, d in enumerate(dias_semana):
    cols[i].markdown(f"**{d}**")

coluna = primeiro_dia
for dia in range(1, total_dias + 1):
    dia_semana = datetime(st.session_state.ano_atual, st.session_state.mes_atual, dia).weekday()
    if dia_semana >= 5:
        continue
    data_str = f"{st.session_state.ano_atual}-{st.session_state.mes_atual:02d}-{dia:02d}"
    qtd = len([a for a in dados["agendamentos"]
               if a["medico"] == medico_nome and a["data"] == data_str])
    
    if qtd == TOTAL_HORARIOS:
        cor = "🟠"
    elif qtd > 0:
        cor = "🟡"
    else:
        cor = "🟢"
    
    with cols[coluna]:
        if st.button(f"{cor} {dia}", key=f"dia_{dia}", use_container_width=True):
            st.session_state.dia_selecionado = dia
            st.session_state.data_selecionada = data_str
    
    coluna += 1
    if coluna > 4:
        coluna = 0

# Ver horários do dia selecionado
if "dia_selecionado" in st.session_state:
    dia_sel = st.session_state.dia_selecionado
    data_sel = st.session_state.data_selecionada
    st.subheader(f"⏰ Horários — {dia_sel:02d}/{st.session_state.mes_atual:02d}/{st.session_state.ano_atual}")
    
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
                with st.expander(f"Editar — {hora}"):
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
                        
                        if st.form_submit_button("💾 Salvar"):
                            idx = dados["agendamentos"].index(ag)
                            dados["agendamentos"][idx] = {
                                "medico": medico_nome, "data": data_sel, "hora": hora,
                                "nome_servidor": nome, "matricula": matricula,
                                "tipo_atendimento": tipo_atend, "tipo_solicitacao": tipo_solic,
                                "observacao": obs, "status": status
                            }
                            salvar_dados(dados)
                            st.success("Salvo!")
                            st.rerun()
        else:
            st.markdown(f"⚪ **{hora}** — Disponível")
            if not st.session_state.eh_leitura:
                with st.expander(f"Agendar — {hora}"):
                    with st.form(f"form_novo_{hora}"):
                        nome = st.text_input("Nome do Servidor")
                        matricula = st.text_input("Matrícula")
                        tipo_atend = st.text_input("Tipo de Atendimento")
                        tipo_solic = st.selectbox("Tipo de Solicitação", opcoes_solicitacao)
                        status = st.selectbox("Status", opcoes_status, index=0)
                        obs = st.text_area("Observação")
                        
                        if st.form_submit_button("✅ Agendar"):
                            if nome and matricula:
                                dados["agendamentos"].append({
                                    "medico": medico_nome, "data": data_sel, "hora": hora,
                                    "nome_servidor": nome, "matricula": matricula,
                                    "tipo_atendimento": tipo_atend, "tipo_solicitacao": tipo_solic,
                                    "observacao": obs, "status": status
                                })
                                salvar_dados(dados)
                                st.success("Agendado!")
                                st.rerun()
                            else:
                                st.warning("Preencha Nome e Matrícula!")
    
    if st.button("❌ Fechar Dia"):
        del st.session_state.dia_selecionado
        del st.session_state.data_selecionada
        st.rerun()