package co.edu.farmacia.vencimientos.infraestructura.transversal;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** JSON mínimo (sin dependencias externas): objetos -> Map, arreglos -> List, números -> Double/Long. */
public final class Json {
    private final String s;
    private int i;

    private Json(String s) { this.s = s; }

    public static Object leer(String texto) {
        if (texto == null || texto.isBlank()) return new LinkedHashMap<String, Object>();
        Json p = new Json(texto);
        Object v = p.valor();
        p.espacios();
        if (p.i != p.s.length()) throw new IllegalArgumentException("JSON inválido");
        return v;
    }

    @SuppressWarnings("unchecked")
    public static Map<String, Object> leerObjeto(String texto) {
        Object v = leer(texto);
        if (!(v instanceof Map)) throw new IllegalArgumentException("Se esperaba un objeto JSON");
        return (Map<String, Object>) v;
    }

    private void espacios() { while (i < s.length() && Character.isWhitespace(s.charAt(i))) i++; }

    private Object valor() {
        espacios();
        if (i >= s.length()) throw new IllegalArgumentException("JSON inválido");
        char c = s.charAt(i);
        if (c == '{') return objeto();
        if (c == '[') return arreglo();
        if (c == '"') return cadena();
        if (s.startsWith("true", i)) { i += 4; return Boolean.TRUE; }
        if (s.startsWith("false", i)) { i += 5; return Boolean.FALSE; }
        if (s.startsWith("null", i)) { i += 4; return null; }
        return numero();
    }

    private Map<String, Object> objeto() {
        Map<String, Object> m = new LinkedHashMap<>();
        i++;
        espacios();
        if (s.charAt(i) == '}') { i++; return m; }
        while (true) {
            espacios();
            String k = cadena();
            espacios();
            if (s.charAt(i++) != ':') throw new IllegalArgumentException("JSON inválido");
            m.put(k, valor());
            espacios();
            char c = s.charAt(i++);
            if (c == '}') return m;
            if (c != ',') throw new IllegalArgumentException("JSON inválido");
        }
    }

    private List<Object> arreglo() {
        List<Object> l = new ArrayList<>();
        i++;
        espacios();
        if (s.charAt(i) == ']') { i++; return l; }
        while (true) {
            l.add(valor());
            espacios();
            char c = s.charAt(i++);
            if (c == ']') return l;
            if (c != ',') throw new IllegalArgumentException("JSON inválido");
        }
    }

    private String cadena() {
        if (s.charAt(i) != '"') throw new IllegalArgumentException("JSON inválido");
        StringBuilder b = new StringBuilder();
        i++;
        while (true) {
            char c = s.charAt(i++);
            if (c == '"') return b.toString();
            if (c == '\\') {
                char e = s.charAt(i++);
                switch (e) {
                    case 'n' -> b.append('\n');
                    case 't' -> b.append('\t');
                    case 'r' -> b.append('\r');
                    case 'b' -> b.append('\b');
                    case 'f' -> b.append('\f');
                    case 'u' -> { b.append((char) Integer.parseInt(s.substring(i, i + 4), 16)); i += 4; }
                    default -> b.append(e);
                }
            } else b.append(c);
        }
    }

    private Object numero() {
        int ini = i;
        while (i < s.length() && "+-0123456789.eE".indexOf(s.charAt(i)) >= 0) i++;
        String n = s.substring(ini, i);
        if (n.isEmpty()) throw new IllegalArgumentException("JSON inválido");
        return (n.contains(".") || n.contains("e") || n.contains("E")) ? (Object) Double.valueOf(n) : (Object) Long.valueOf(n);
    }

    public static String escribir(Object v) {
        StringBuilder b = new StringBuilder();
        escribir(v, b);
        return b.toString();
    }

    private static void escribir(Object v, StringBuilder b) {
        if (v == null) b.append("null");
        else if (v instanceof Map<?, ?> m) {
            b.append('{');
            boolean primero = true;
            for (Map.Entry<?, ?> e : m.entrySet()) {
                if (!primero) b.append(',');
                primero = false;
                escribir(String.valueOf(e.getKey()), b);
                b.append(':');
                escribir(e.getValue(), b);
            }
            b.append('}');
        } else if (v instanceof Iterable<?> l) {
            b.append('[');
            boolean primero = true;
            for (Object o : l) {
                if (!primero) b.append(',');
                primero = false;
                escribir(o, b);
            }
            b.append(']');
        } else if (v instanceof Number || v instanceof Boolean) b.append(v);
        else {
            b.append('"');
            for (char c : v.toString().toCharArray()) {
                switch (c) {
                    case '"' -> b.append("\\\"");
                    case '\\' -> b.append("\\\\");
                    case '\n' -> b.append("\\n");
                    case '\r' -> b.append("\\r");
                    case '\t' -> b.append("\\t");
                    default -> { if (c < 0x20) b.append(String.format("\\u%04x", (int) c)); else b.append(c); }
                }
            }
            b.append('"');
        }
    }
}
