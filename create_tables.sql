-- Script para criar tabelas do Sistema de Controle de EPI - IURD
-- MySQL

CREATE DATABASE IF NOT EXISTS Universal_Epi;
USE Universal_Epi;

-- Tabela EPI
CREATE TABLE IF NOT EXISTS epi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ca VARCHAR(50) UNIQUE NOT NULL,
    descricao TEXT NOT NULL,
    foto VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela Colaborador
CREATE TABLE IF NOT EXISTS colaborador (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_completo VARCHAR(255) NOT NULL,
    matricula VARCHAR(50) UNIQUE NOT NULL,
    funcao VARCHAR(100) NOT NULL,
    setor VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela RegistroEPI
CREATE TABLE IF NOT EXISTS registro_epi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    colaborador_id INT NOT NULL,
    epi_id INT NOT NULL,
    data_retirada DATETIME NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    FOREIGN KEY (colaborador_id) REFERENCES colaborador(id) ON DELETE CASCADE,
    FOREIGN KEY (epi_id) REFERENCES epi(id) ON DELETE CASCADE
);
