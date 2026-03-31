import numpy as np
import pandas as pd
import io

def carregar_dados_nsp(caminho_arquivo):
    secoes = {}
    secao_atual = None
    buffer_linhas = []

    with open(caminho_arquivo, 'r') as f:
        for linha in f:
            linha = linha.strip()
            
            # Pula linhas vazias ou apenas comentários
            if not linha or (linha.startswith('#') and not linha.startswith('# ID') and not linha.startswith('# ShiftID') and not linha.startswith('# EmployeeID')
                             and not linha.startswith('# Day')):
                continue
                
            # Identifica nova seção
            if linha.startswith('SECTION_'):
                if secao_atual:
                    secoes[secao_atual] = buffer_linhas
                secao_atual = linha
                buffer_linhas = []
                continue
            
            buffer_linhas.append(linha)
            
        # Adiciona a última seção
        if secao_atual:
            secoes[secao_atual] = buffer_linhas

    # --- Transformando cada seção em DataFrame ---
    
    # 1. Horizon (Valor único)
    horizon = int(secoes['SECTION_HORIZON'][0])

    # 2. Shifts
    df_shifts = pd.read_csv(io.StringIO('\n'.join(secoes['SECTION_SHIFTS'])))
    
    # 3. Staff
    df_staff = pd.read_csv(io.StringIO('\n'.join(secoes['SECTION_STAFF'])))

    # 4. Days Off
    df_days_off = pd.read_csv(io.StringIO('\n'.join(secoes['SECTION_DAYS_OFF'])))

    # 5. Requests (On e Off)
    df_on_requests = pd.read_csv(io.StringIO('\n'.join(secoes['SECTION_SHIFT_ON_REQUESTS'])))
    df_off_requests = pd.read_csv(io.StringIO('\n'.join(secoes['SECTION_SHIFT_OFF_REQUESTS'])))

    # 6. Cover (Demanda)
    df_cover = pd.read_csv(io.StringIO('\n'.join(secoes['SECTION_COVER'])))

    return horizon, df_shifts, df_staff, df_days_off, df_on_requests, df_off_requests, df_cover

def aux_staff(df):
    res = {}

    for _, row in df.iterrows():
        # 1. Pegamos o ID (ex: 'A')
        id_val = row[df.columns[0]]
        
        # 2. Partimos a string 'E=28|D=28|L=0' pelos '|'
        shifts = row[df.columns[1]].split('|')
        
        for s in shifts:
            # 3. Partimos cada pedaço pelo '=' (ex: 'E=28')
            key, val = s.split('=')
            
            # 4. Adicionamos ao dict como tuplo (ID, Shift)
            res[(id_val, key)] = int(val)
    
    return res

def teste1(dic,n):

    for el in dic.keys():
        dic[el] = n*dic[el]

    return dic


def dados(n_instancia):

    caminho_arquivo = r"Instancias/Instance" + str(n_instancia) + ".txt"
    horizon, df_shifts, df_staff, df_days_off, df_on_requests, df_off_requests, df_cover = carregar_dados_nsp(caminho_arquivo)
    
    I = df_staff[df_staff.columns[0]].to_list()
    h = horizon
    D = range(h)
    W = range((int(h) // 7))
    T = df_shifts[df_shifts.columns[0]].to_list()

    if n_instancia == 1:
        Rt = {}
    else:
        Rt = df_shifts.set_index(df_shifts.columns[0])[df_shifts.set_index(df_shifts.columns[0]).columns[1]].str.split('|').to_dict()
    Rt = {k: v for k, v in Rt.items() if not (isinstance(v, float) and pd.isna(v))}

    if n_instancia in [1, 2, 3]:
        Ni = df_days_off.groupby(df_days_off.columns[0])[df_days_off.columns[1]].apply(list).to_dict()
    else:
        Ni =  {k: v.tolist() for k, v in df_days_off.iterrows()}


    lt = df_shifts.set_index(df_shifts.columns[0])[df_shifts.set_index(df_shifts.columns[0]).columns[0]].to_dict()
    max_it = aux_staff(df_staff)
    bmin_i = df_staff.set_index(df_staff.columns[0])[df_staff.set_index(df_staff.columns[0]).columns[2]].to_dict()
    bmax_i = df_staff.set_index(df_staff.columns[0])[df_staff.set_index(df_staff.columns[0]).columns[1]].to_dict()
    cmin_i = df_staff.set_index(df_staff.columns[0])[df_staff.set_index(df_staff.columns[0]).columns[4]].to_dict()
    cmax_i = df_staff.set_index(df_staff.columns[0])[df_staff.set_index(df_staff.columns[0]).columns[3]].to_dict()
    omin_i = df_staff.set_index(df_staff.columns[0])[df_staff.set_index(df_staff.columns[0]).columns[5]].to_dict()
    amax_i = df_staff.set_index(df_staff.columns[0])[df_staff.set_index(df_staff.columns[0]).columns[6]].to_dict()
    q_idt = df_on_requests.set_index([df_on_requests.columns[0],df_on_requests.columns[1],df_on_requests.columns[2]])[df_on_requests.columns[3]].to_dict()
    p_idt = df_off_requests.set_index([df_off_requests.columns[0],df_off_requests.columns[1],df_off_requests.columns[2]])[df_off_requests.columns[3]].to_dict()
    u_dt =  df_cover.set_index([df_cover.columns[0],df_cover.columns[1]])[df_cover.columns[2]].to_dict()
    vmin_dt = df_cover.set_index([df_cover.columns[0],df_cover.columns[1]])[df_cover.columns[3]].to_dict()
    vmin_dt = teste1(vmin_dt,1)
    vmax_dt = df_cover.set_index([df_cover.columns[0],df_cover.columns[1]])[df_cover.columns[4]].to_dict()
    vmax_dt = teste1(vmax_dt,1)

    return I,h,D,W,T,Rt,Ni,lt,max_it,bmin_i,bmax_i,cmin_i,cmax_i,omin_i,amax_i,q_idt,p_idt,u_dt,vmin_dt,vmax_dt