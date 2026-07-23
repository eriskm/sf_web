CREATE DATABASE IF NOT EXISTS db_ais_systems;
USE db_ais_systems;

CREATE TABLE IF NOT EXISTS arsip_garansi (
    id_garansi INT AUTO_INCREMENT PRIMARY KEY,
    nama_user VARCHAR(100),
    device VARCHAR(100),
    tgl_akhir DATE
);

CREATE TABLE IF NOT EXISTS arsip_pelanggan (
    id_arsip INT AUTO_INCREMENT PRIMARY KEY,
    nama_user VARCHAR(100),
    device VARCHAR(100),
    tindakan TEXT
);

CREATE TABLE IF NOT EXISTS data_sparepart (
    id_sparepart INT AUTO_INCREMENT PRIMARY KEY,
    kategori VARCHAR(50),
    merek VARCHAR(50),
    jenis_barang VARCHAR(100),
    jenis_device VARCHAR(100),
    qty INT DEFAULT 0
);
