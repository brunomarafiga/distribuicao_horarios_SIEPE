
import re
import pandas as pd
import datetime
import zipfile
import os

def limpar_texto(val):
    if pd.isna(val):
        return ""
    texto = str(val).strip()
    texto = re.sub(r'(\d+)[\\?]\s*-\s*', r'\1ª - ', texto)
    texto = texto.replace('ÁÁrea', 'Área')
    if 'Área' not in texto and 'rea' in texto:
        texto = texto.replace('rea', 'Área')
    if 'temática' not in texto and 'temtica' in texto:
        texto = texto.replace('temtica', 'temática')
    texto = texto.replace('apresentao', 'apresentação').replace('Programao', 'Programação')
    texto = texto.replace('Situao', 'Situação').replace('Lngua', 'Língua')
    texto = texto.replace('Nmero', 'Número').replace('Ttulo', 'Título')
    return texto

def normalizar_titulos(texto):
    if not isinstance(texto, str) or not texto.strip(): return texto
    texto = texto.lower()
    words = texto.split()
    lower_words = {"de", "da", "do", "das", "dos", "e", "em", "na", "no", "nas", "nos", "a", "o", "as", "os", "com", "por", "para"}
    new_words = []
    for i, w in enumerate(words):
        if w in lower_words and i > 0:
            new_words.append(w)
        else:
            new_words.append(w.capitalize())
    return " ".join(new_words)

def extrair_modalidade(p):
    if not p or pd.isna(p) or str(p).strip() == "":
        return "Comunicação Oral"
    p_str = str(p).strip()
    if p_str.startswith("1:Oficina") or p_str == "Oficina":
        return "Oficina"
    elif "Oficina" in p_str and ("Roda de conversa" not in p_str or p_str.find("Oficina") < p_str.find("Roda de conversa")):
        return "Oficina"
    else:
        return "Comunicação Oral"

def normalizar_dataframe(df):
    col_map = {}
    for col in df.columns:
        clean = limpar_texto(col)
        col_map[col] = clean
    df = df.rename(columns=col_map)
    
    num_col = next((c for c in df.columns if 'n' in c.lower() and 'mero' in c.lower()), 'Número')
    tit_col = next((c for c in df.columns if 't' in c.lower() and 'tulo' in c.lower()), 'Título')
    cpf_col = next((c for c in df.columns if 'cpf' in c.lower()), 'CPF Submissor')
    sub_col = next((c for c in df.columns if 'submissor' in c.lower() and 'cpf' not in c.lower()), 'Submissor')
    
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].apply(limpar_texto)
            
    if tit_col in df.columns:
        df[tit_col] = df[tit_col].apply(normalizar_titulos)
            
    return df, num_col, tit_col, cpf_col, sub_col

def gerar_slots(hora_str, capacidade):
    t = datetime.datetime.strptime(hora_str, "%H:%M")
    slots = []
    delta = 80 // capacidade 
    for i in range(capacidade):
        slots.append((t + datetime.timedelta(minutes=i*delta)).strftime("%H:%M"))
    return slots

def gerar_ensalamento(
    input_file="lista de resumos.xls",
    output_excel="ensalamento_curitiba_971.xlsx",
    output_csv="ensalamento_curitiba_971.csv",
    output_resumos_csv="horarios_salas_resumos.csv",
    output_zip="03_Distribuicao_Horarios_SIEPE.zip",
    limite_curitiba=971
):
    print("=" * 60)
    print(f"INICIANDO ENSALAMENTO OFICIAL SIEPE - {limite_curitiba} Trabalhos")
    print("=" * 60)
    
    if not os.path.exists(input_file):
        if os.path.exists("../lista de resumos.xls"):
            input_file = "../lista de resumos.xls"
        elif os.path.exists("Trabalhos (2).xls"):
            input_file = "Trabalhos (2).xls"

    horarios_sessoes = {
        1: {"nome": "Sessão 1 (Manhã)", "turno": "Manhã", "inicio": "08:20", "fim": "10:00"},
        2: {"nome": "Sessão 2 (Manhã)", "turno": "Manhã", "inicio": "10:30", "fim": "12:10"},
        3: {"nome": "Sessão 3 (Tarde)", "turno": "Tarde", "inicio": "14:00", "fim": "15:40"},
        4: {"nome": "Sessão 4 (Tarde)", "turno": "Tarde", "inicio": "16:10", "fim": "17:50"},
        5: {"nome": "Sessão 5 (Noite)", "turno": "Noite", "inicio": "19:00", "fim": "20:40"}
    }

    grade_semanal = [
        {"dia": "Segunda-feira", "data_ref": "20/10", "sessoes": [3, 4, 5]},
        {"dia": "Terça-feira",   "data_ref": "21/10", "sessoes": [1, 2, 3, 4, 5]},
        {"dia": "Quarta-feira",  "data_ref": "22/10", "sessoes": [1, 2, 3, 4, 5]},
        {"dia": "Quinta-feira",  "data_ref": "23/10", "sessoes": [1, 2, 3, 4, 5]},
        {"dia": "Sexta-feira",   "data_ref": "24/10", "sessoes": [1, 2, 3, 4]}
    ]

    salas_curitiba = [
        ("Ciências da Terra", "CT01"), ("Ciências da Terra", "CT02"), ("Ciências da Terra", "CT03"),
        ("Ciências da Terra", "CT05"), ("Ciências da Terra", "CT06"),
        ("Ciências Exatas", "PA-03"), ("Ciências Exatas", "PA-04"), ("Ciências Exatas", "PA-05"),
        ("Ciências Exatas", "PA-07"), ("Ciências Exatas", "PA-08"), ("Ciências Exatas", "PA-09")
    ]

    epex_file = "EPEx-PG.xls"
    if not os.path.exists(epex_file):
        if os.path.exists("../EPEx-PG.xls"):
            epex_file = "../EPEx-PG.xls"
        elif os.path.exists("/home/bruno_marafiga/Downloads/EPEx-PG.xls"):
            epex_file = "/home/bruno_marafiga/Downloads/EPEx-PG.xls"

    df_raw = pd.read_excel(input_file)
    df, num_col, tit_col, cpf_col, sub_col = normalizar_dataframe(df_raw)
    
    # Carregar dados reais do EPEx-PG.xls (filtrando Projeto de Extensão na Pós-Graduação)
    if os.path.exists(epex_file):
        df_epex_raw = pd.read_excel(epex_file)
        df_epex, _, _, _, _ = normalizar_dataframe(df_epex_raw)
        prog_col_epex = next((c for c in df_epex.columns if 'programa' in c.lower()), 'Programa Institucional')
        df_epex_ext = df_epex[df_epex[prog_col_epex].astype(str).str.contains('Projeto de Extensão na Pós-Graduação', case=False, na=False)].copy()
        df_epex_ext['Evento'] = '2ª - EPEx-PG'
        print(f"Carregados {len(df_epex_ext)} trabalhos reais do EPEx-PG (Projeto de Extensão na Pós-Graduação)")
        df = pd.concat([df, df_epex_ext], ignore_index=True)

    pref_col = next((c for c in df.columns if 'preferencia' in c.lower()), None)
    if pref_col:
        df['Modalidade'] = df[pref_col].apply(extrair_modalidade)
    else:
        df['Modalidade'] = "Comunicação Oral"

    other_campi = ["litoral", "palotina", "jandaia", "toledo", "pontal", "estudos do mar", "maringá"]
    def real_city(row):
        setor = str(row.get("Setor", "")).lower()
        for c in other_campi:
            if c in setor:
                return c
        return "curitiba"
    
    df["Real_City"] = df.apply(real_city, axis=1)

    def is_pet_litoral(row):
        prog = str(row.get('Programa Institucional', '')).lower()
        setor = str(row.get('Setor', '')).lower()
        return ('pet' in prog) and ('litoral' in setor)

    def is_epex_ext(row):
        prog = str(row.get('Programa Institucional', '')).lower()
        ev = str(row.get('Evento', '')).lower()
        return ('projeto de extensão na pós-graduação' in prog) or ('epex' in ev)

    df['Is_PET_Litoral'] = df.apply(is_pet_litoral, axis=1)
    df['Is_EPEX'] = df.apply(is_epex_ext, axis=1)
    
    df_curitiba = df[(df["Real_City"] == "curitiba") | df['Is_PET_Litoral'] | df['Is_EPEX']].copy()

    ids_demanda01 = [202626287, 202623116, 202623832, 202624396, 202625680]
    def is_demanda01(row):
        try:
            num = int(row.get(num_col, 0))
            if num in ids_demanda01: return True
        except: pass
        sub = str(row.get(sub_col, '')).upper()
        if 'EVERTON RIBEIRO' in sub: return True
        return False
    df_curitiba['Is_Demanda01'] = df_curitiba.apply(is_demanda01, axis=1)

    df_prio = df_curitiba[df_curitiba['Is_Demanda01'] | df_curitiba['Is_PET_Litoral'] | df_curitiba['Is_EPEX']].copy()
    df_outros = df_curitiba[~(df_curitiba['Is_Demanda01'] | df_curitiba['Is_PET_Litoral'] | df_curitiba['Is_EPEX'])].copy()
    
    sort_cols = ['Modalidade']
    area_col = next((c for c in df_curitiba.columns if 'rea' in c.lower()), 'Área temática')
    if area_col in df_curitiba.columns: sort_cols.append(area_col)
    sort_cols.extend(['Evento', 'Programa Institucional', tit_col])
    
    df_outros_ordenados = df_outros.sort_values(by=sort_cols, na_position='last')
    
    df_curitiba_selecionados = pd.concat([df_prio, df_outros_ordenados], ignore_index=True)
    if len(df_curitiba_selecionados) > limite_curitiba:
        df_curitiba_selecionados = df_curitiba_selecionados.iloc[:limite_curitiba].copy()
        
    total_selecionado = len(df_curitiba_selecionados)
    print(f"Total de trabalhos selecionados para Curitiba: {total_selecionado}")

    total_room_sessions = sum(len(d["sessoes"]) for d in grade_semanal) * len(salas_curitiba) # 242
    dict_cap = {}
    for dia_info in grade_semanal:
        for s in dia_info["sessoes"]:
            for p, sl in salas_curitiba:
                dict_cap[(dia_info["dia"], s, p, sl)] = 4
                
    excedente = total_selecionado - (total_room_sessions * 4)
    if excedente > 0:
        ordem_prioridade = [
            ("Segunda-feira", 3, "Ciências da Terra", "CT01"),
            ("Segunda-feira", 3, "Ciências Exatas", "PA-03"),
            ("Terça-feira", 1, "Ciências Exatas", "PA-04")
        ]
        for k in ordem_prioridade:
            if excedente > 0 and k in dict_cap:
                dict_cap[k] += 1
                excedente -= 1
        for k in dict_cap:
            if excedente <= 0: break
            if dict_cap[k] == 4:
                dict_cap[k] += 1
                excedente -= 1

    alocacoes = []
    apresentadores_ocupados = set()
    
    df_pet_lit = df_curitiba_selecionados[df_curitiba_selecionados['Is_PET_Litoral']].copy().reset_index(drop=True)
    df_dem01 = df_curitiba_selecionados[df_curitiba_selecionados['Is_Demanda01']].copy().reset_index(drop=True)
    df_geral = df_curitiba_selecionados[(~df_curitiba_selecionados['Is_PET_Litoral']) & (~df_curitiba_selecionados['Is_Demanda01'])].copy().reset_index(drop=True)

    dia_pet, sessao_pet_id = "Segunda-feira", 3
    salas_ct = [s for s in salas_curitiba if s[0] == "Ciências da Terra"]
    
    idx_pet = 0
    total_pet = len(df_pet_lit)
    for predio, sala in salas_ct:
        if idx_pet >= total_pet: break
        cap_sala_local = dict_cap[(dia_pet, sessao_pet_id, predio, sala)]
        slots_horarios = gerar_slots(horarios_sessoes[sessao_pet_id]['inicio'], cap_sala_local)
        
        for ordem in range(1, cap_sala_local + 1):
            if idx_pet >= total_pet: break
            row = df_pet_lit.iloc[idx_pet].to_dict()
            row['Dia'] = dia_pet
            row['Sessao'] = f"Sessão {sessao_pet_id}"
            row['Turno'] = horarios_sessoes[sessao_pet_id]['turno']
            row['Predio'] = predio
            row['Sala'] = sala
            row['Ordem'] = ordem
            row['Horario_Inicio'] = slots_horarios[ordem - 1]
            row['Duracao_Min'] = "20 min (exposição) + 20 min (debate final)" if cap_sala_local == 4 else "16 min (exposição) + 20 min (debate final)"
            alocacoes.append(row)
            apres_id = str(row.get(cpf_col) or row.get(sub_col) or '').strip()
            if apres_id: apresentadores_ocupados.add((dia_pet, sessao_pet_id, apres_id))
            idx_pet += 1

    dia_dem01, sessao_dem01_id = "Segunda-feira", 3
    predio_dem01, sala_dem01 = "Ciências Exatas", "PA-03"
    cap_dem01 = dict_cap[(dia_dem01, sessao_dem01_id, predio_dem01, sala_dem01)]
    slots_dem01 = gerar_slots(horarios_sessoes[sessao_dem01_id]['inicio'], cap_dem01)
    
    for ordem, (_, row_data) in enumerate(df_dem01.iterrows(), start=1):
        if ordem > cap_dem01: break
        row = row_data.to_dict()
        row['Dia'] = dia_dem01
        row['Sessao'] = f"Sessão {sessao_dem01_id}"
        row['Turno'] = horarios_sessoes[sessao_dem01_id]['turno']
        row['Predio'] = predio_dem01
        row['Sala'] = sala_dem01
        row['Ordem'] = ordem
        row['Horario_Inicio'] = slots_dem01[ordem - 1]
        row['Duracao_Min'] = "20 min (exposição) + 20 min (debate final)" if cap_dem01 == 4 else "16 min (exposição) + 20 min (debate final)"
        alocacoes.append(row)
        apres_id = str(row.get(cpf_col) or row.get(sub_col) or '').strip()
        if apres_id: apresentadores_ocupados.add((dia_dem01, sessao_dem01_id, apres_id))

    salas_ocupadas_previamente = {}
    for s_idx, (predio, sala) in enumerate(salas_ct):
        cap_sala_local = dict_cap[(dia_pet, sessao_pet_id, predio, sala)]
        qtd_alocada = min(cap_sala_local, max(0, total_pet - sum([dict_cap[(dia_pet, sessao_pet_id, salas_ct[i][0], salas_ct[i][1])] for i in range(s_idx)])))
        if qtd_alocada > 0: salas_ocupadas_previamente[(dia_pet, sessao_pet_id, predio, sala)] = qtd_alocada
        
    salas_ocupadas_previamente[(dia_dem01, sessao_dem01_id, predio_dem01, sala_dem01)] = len(df_dem01)

    lista_geral_trabalhos = df_geral.to_dict('records')
    
    salas_assig = {}
    for dia_info in grade_semanal:
        dia = dia_info["dia"]
        for sessao_id in dia_info["sessoes"]:
            for predio, sala in salas_curitiba:
                salas_assig[(dia, sessao_id, predio, sala)] = []

    for a in alocacoes:
        dia = a['Dia']
        sessao_id = int(a['Sessao'].replace('Sessão ', ''))
        predio = a['Predio']
        sala = a['Sala']
        if (dia, sessao_id, predio, sala) in salas_assig:
            salas_assig[(dia, sessao_id, predio, sala)].append(a)

    for trab in lista_geral_trabalhos:
        apres_id = str(trab.get(cpf_col) or trab.get(sub_col) or '').strip()
        area = trab.get(area_col, '')
        
        best_score = -999999
        best_k = None
        
        for k, cap in dict_cap.items():
            dia, sessao_id, predio, sala = k
            if len(salas_assig[k]) >= cap:
                continue
                
            if apres_id and (dia, sessao_id, apres_id) in apresentadores_ocupados:
                continue
                
            score = 0
            if len(salas_assig[k]) > 0:
                areas_in_room = [w.get(area_col, '') for w in salas_assig[k]]
                if area in areas_in_room:
                    score += 1000
                else:
                    score -= 1000
            else:
                score += 500
                
            dia_idx = {"Segunda-feira":0, "Terça-feira":1, "Quarta-feira":2, "Quinta-feira":3, "Sexta-feira":4}[dia]
            score -= (dia_idx * 10 + sessao_id)
            
            if score > best_score:
                best_score = score
                best_k = k
                
        if best_k is None:
            best_score = -999999
            for k, cap in dict_cap.items():
                dia, sessao_id, predio, sala = k
                if len(salas_assig[k]) >= cap:
                    continue
                score = 0
                if len(salas_assig[k]) > 0:
                    areas_in_room = [w.get(area_col, '') for w in salas_assig[k]]
                    if area in areas_in_room: score += 1000
                    else: score -= 1000
                else:
                    score += 500
                dia_idx = {"Segunda-feira":0, "Terça-feira":1, "Quarta-feira":2, "Quinta-feira":3, "Sexta-feira":4}[dia]
                score -= (dia_idx * 10 + sessao_id)
                if score > best_score:
                    best_score = score
                    best_k = k
                    
        if best_k is not None:
            dia, sessao_id, predio, sala = best_k
            cap_sala_local = dict_cap[best_k]
            ordem = len(salas_assig[best_k]) + 1
            slots_horarios = gerar_slots(horarios_sessoes[sessao_id]['inicio'], cap_sala_local)
            
            row = dict(trab)
            row['Dia'] = dia
            row['Sessao'] = f"Sessão {sessao_id}"
            row['Turno'] = horarios_sessoes[sessao_id]['turno']
            row['Predio'] = predio
            row['Sala'] = sala
            row['Ordem'] = ordem
            row['Horario_Inicio'] = slots_horarios[ordem - 1]
            row['Duracao_Min'] = "20 min (exposição) + 20 min (debate final)" if cap_sala_local == 4 else "16 min (exposição) + 20 min (debate final)"
            
            alocacoes.append(row)
            salas_assig[best_k].append(row)
            if apres_id: apresentadores_ocupados.add((dia, sessao_id, apres_id))
        else:
            print(f"ERRO CRÍTICO: Impossível alocar trabalho")

    df_resultado = pd.DataFrame(alocacoes)
    
    # Criar coluna 'Código do Resumo' e preencher 'Bloco'
    df_resultado['Código do Resumo'] = df_resultado[num_col]
    df_resultado['Bloco'] = df_resultado['Predio']


    colunas_principais = ['Dia', 'Sessao', 'Turno', 'Horario_Inicio', 'Bloco', 'Predio', 'Sala', 'Ordem', 'Duracao_Min', 'Evento', 'Código do Resumo', tit_col, sub_col, 'Área temática', 'Modalidade', 'Programa Institucional', 'Setor']
    colunas_existentes = []
    for c in colunas_principais:
        if c in df_resultado.columns and c not in colunas_existentes:
            colunas_existentes.append(c)

    outras_colunas = [c for c in df_resultado.columns if c not in colunas_existentes and not c.startswith('Is_') and c != 'Real_City']
    df_resultado_final = df_resultado[colunas_existentes + outras_colunas]

    # Salvar CSV Completo
    df_resultado_final.to_csv(output_csv, index=False, encoding='utf-8-sig', sep=';')
    
    # Salvar Excel Completo
    ordem_dias = {"Segunda-feira": 1, "Terça-feira": 2, "Quarta-feira": 3, "Quinta-feira": 4, "Sexta-feira": 5}
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df_resultado_final.to_excel(writer, sheet_name="Ensalamento Curitiba", index=False)
        resumo_sessao = df_resultado_final.groupby(['Dia', 'Sessao', 'Turno']).size().reset_index(name='Total_Apresentacoes')
        resumo_sessao['Dia_Num'] = resumo_sessao['Dia'].map(ordem_dias)
        resumo_sessao = resumo_sessao.sort_values(by=['Dia_Num', 'Sessao']).drop(columns=['Dia_Num'])
        resumo_sessao.to_excel(writer, sheet_name="Resumo Sessões", index=False)
        resumo_salas = df_resultado_final.groupby(['Bloco', 'Sala']).size().reset_index(name='Total_Apresentacoes')
        resumo_salas.to_excel(writer, sheet_name="Resumo Salas", index=False)

    # Salvar CSV Simplificado "horarios_salas_resumos.csv" com Código do Resumo, Bloco, Área e Modalidade
    cols_simplificadas = ['Dia', 'Sessao', 'Turno', 'Horario_Inicio', 'Bloco', 'Sala', 'Ordem', 'Evento', 'Código do Resumo', tit_col, sub_col, 'Área temática', 'Modalidade']
    cols_simplificadas_existentes = [c for c in cols_simplificadas if c in df_resultado_final.columns]
    df_resumos = df_resultado_final[cols_simplificadas_existentes].rename(columns={
        tit_col: 'Título',
        sub_col: 'Submissor',
        'Área temática': 'Área'
    })
    df_resumos.to_csv(output_resumos_csv, index=False, encoding='utf-8-sig', sep=';')
    print(f"Gerado {output_resumos_csv} com {len(df_resumos)} registros.")


    # Atualizar o ZIP com as sessões
    print("Atualizando ZIP com ensalamentos por sessão...")
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for (dia, sessao), group in df_resultado_final.groupby(['Dia', 'Sessao']):
            filename = f"{dia}_{sessao.replace(' ', '_')}.csv"
            csv_data = group.to_csv(index=False, encoding='utf-8-sig', sep=';')
            zipf.writestr(f"Distribuicao_Horarios/{dia}/{filename}", csv_data)

    print(f"Total final alocado: {len(df_resultado_final)}")
    return df_resultado_final

if __name__ == "__main__":
    gerar_ensalamento()
