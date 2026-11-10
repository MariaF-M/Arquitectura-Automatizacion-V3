package co.edu.farmacia.vencimientos.dominio.modelo;

import java.time.LocalDate;

/** Memento (GoF): foto inmutable del estado de AlertaVencimiento. */
public record AlertaVencimientoMemento(String id, String loteCodigo, LocalDate fechaVencimiento, Integer diasParaVencer, Integer prioridadFefo, String semaforo, String estado, String motivo) { }
