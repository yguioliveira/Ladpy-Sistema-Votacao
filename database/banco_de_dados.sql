-- ============================================================
-- BANCO DE DADOS - PROJETO INTEGRADOR
-- Sistema de Votacao Digital
-- ============================================================

CREATE DATABASE IF NOT EXISTS projetointegrador_db;

USE projetointegrador_db;

-- ============================================================
-- TABELA: ELEITORES
-- Armazena os eleitores cadastrados no sistema.
-- O CPF e a chave de acesso sao armazenados criptografados.
-- ============================================================

CREATE TABLE IF NOT EXISTS eleitores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_completo VARCHAR(255) NOT NULL,
    cpf_criptografado VARCHAR(255) NOT NULL UNIQUE,
    titulo_eleitor VARCHAR(20) NOT NULL UNIQUE,
    e_mesario ENUM('Sim', 'Nao') NOT NULL DEFAULT 'Nao',
    chave_acesso_criptografada VARCHAR(255) NOT NULL,
    status_voto ENUM('NAO_VOTOU', 'JA_VOTOU') DEFAULT 'NAO_VOTOU',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABELA: CANDIDATOS
-- Armazena os candidatos disponiveis para votacao.
-- O numero do candidato deve ser unico.
-- ============================================================

CREATE TABLE IF NOT EXISTS candidatos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    numero INT NOT NULL UNIQUE,
    partido VARCHAR(100) NOT NULL
);

-- ============================================================
-- TABELA: VOTOS
-- Armazena os votos registrados no sistema.
-- O candidato_id pode ser NULL para representar voto nulo.
-- O protocolo de votacao e armazenado criptografado.
-- ============================================================

CREATE TABLE IF NOT EXISTS votos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidato_id INT NULL,
    data_hora DATETIME NOT NULL,
    protocolo_criptografado VARCHAR(255) NOT NULL,

    FOREIGN KEY (candidato_id) REFERENCES candidatos(id)
);

-- ============================================================
-- TABELA: LOGS
-- Armazena os eventos criticos do processo de votacao.
-- Exemplos: abertura, alertas, votos realizados e encerramento.
-- ============================================================

CREATE TABLE IF NOT EXISTS logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_hora DATETIME NOT NULL,
    tipo ENUM('ABERTURA', 'ALERTA', 'SUCESSO', 'ENCERRAMENTO') NOT NULL,
    descricao TEXT NOT NULL
);

-- ============================================================
-- TABELA: CONTROLE_VOTACAO
-- Controla o estado da urna: ABERTA ou FECHADA.
-- Deve possuir apenas um registro principal com id = 1.
-- ============================================================

CREATE TABLE IF NOT EXISTS controle_votacao (
    id INT PRIMARY KEY,
    status VARCHAR(20) NOT NULL,
    aberto_em DATETIME NULL,
    encerrado_em DATETIME NULL
);

INSERT IGNORE INTO controle_votacao (id, status)
VALUES (1, 'FECHADA');

-- ============================================================
-- DADOS INICIAIS: CANDIDATOS
-- Registros usados para testes e demonstracao do sistema.
-- ============================================================

INSERT IGNORE INTO candidatos (nome, numero, partido)
VALUES
('Mariana Costa', 10, 'PAC'),
('Roberto Almeida', 22, 'UPD'),
('Fernanda Rocha', 35, 'PJS'),
('Lucas Martins', 44, 'MPT'),
('Patricia Nunes', 55, 'NOV');

-- ============================================================
-- DADOS INICIAIS: ELEITORES
-- CPFs e chaves ja estao criptografados conforme a Cifra de Hill.
--
-- Chaves originais para teste:
-- Ana Silva: ANS1234
-- Bruno Santos: BRS2345
-- Carla Oliveira: CAO3456
-- Diego Souza: DIS4567
-- Eduarda Lima: EDL5678
-- ============================================================

INSERT IGNORE INTO eleitores
(nome_completo, cpf_criptografado, titulo_eleitor, e_mesario, chave_acesso_criptografada, status_voto, criado_em)
VALUES
('Ana Silva', 'JMVAHOTCBSCL', '102385010671', 'Sim', 'NNFPPTYC', 'NAO_VOTOU', NOW()),
('Bruno Santos', 'ZGNSBEPQDCAA', '004356870906', 'Nao', 'CJIUVAEJ', 'NAO_VOTOU', NOW()),
('Carla Oliveira', 'VUCLEASYBYEJ', '123456781490', 'Nao', 'GEZRBHKQ', 'NAO_VOTOU', NOW()),
('Diego Souza', 'GHPWYCQXEDEJ', '876543212020', 'Nao', 'HUOEHOQX', 'NAO_VOTOU', NOW()),
('Eduarda Lima', 'KHBEGHVATCAA', '555123452666', 'Nao', 'VXWVNVWE', 'NAO_VOTOU', NOW());

-- ============================================================
-- CONSULTAS DE VERIFICACAO
-- Use estes comandos para conferir os dados cadastrados.
-- ============================================================

SELECT * FROM eleitores;
SELECT * FROM candidatos;
SELECT * FROM votos;
SELECT * FROM logs;
SELECT * FROM controle_votacao;
