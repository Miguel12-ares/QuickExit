-- Añadir columna id_instructor_lider a la tabla FICHAS
ALTER TABLE FICHAS
ADD COLUMN id_instructor_lider INT,
ADD CONSTRAINT fk_instructor_lider
FOREIGN KEY (id_instructor_lider) REFERENCES USUARIOS(id_usuario)
ON DELETE SET NULL; 