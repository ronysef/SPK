-- Database: spk_penyewaanmobil

-- DROP DATABASE IF EXISTS spk_penyewaanmobil;

CREATE DATABASE spk_penyewaanmobil
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_Indonesia.1252'
    LC_CTYPE = 'English_Indonesia.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

CREATE TABLE Daftar_Mobil (
	harga_sewa int not null,
	thn_produksi int not null,
	kapasitas int not null,
	kekuatan_mesin int not null,
	konsumsi_bhn_bakar int not null
)
insert into daftar_mobil values 
(600000, 2015, 6, 2000, 19),
(700000, 2017, 5, 1700, 17),
(450000, 2016, 8, 1600, 13),
(500000, 2018, 9, 1800, 14),
(400000, 2019, 7, 1600, 13);