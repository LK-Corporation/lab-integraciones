// CV1 (E-CV-3): arnés mínimo para LinuxForHealth hl7v2-fhir-converter 1.1.1. Convierte cada fichero de <entrada> con la
// llamada pública HL7ToFHIRConverter.convert(String) y escribe <salida>/<nombre>.json, o <nombre>.error con la excepción.
// No toca el mensaje ni el Bundle: el juicio es del verificador. Corre sin red (docker --network none).
import io.github.linuxforhealth.hl7.HL7ToFHIRConverter;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class Arnes {
    public static void main(String[] args) throws Exception {
        Path entrada = Paths.get(args[0]);
        Path salida = Paths.get(args[1]);
        HL7ToFHIRConverter conversor = new HL7ToFHIRConverter();
        java.util.List<Path> ficheros;
        try (Stream<Path> s = Files.list(entrada)) {
            ficheros = s.filter(Files::isRegularFile).sorted().collect(Collectors.toList());
        }
        int bien = 0, mal = 0;
        for (Path f : ficheros) {
            String nombre = f.getFileName().toString();
            String texto = new String(Files.readAllBytes(f), StandardCharsets.UTF_8);
            long t0 = System.nanoTime();
            try {
                String bundle = conversor.convert(texto);
                Files.write(salida.resolve(nombre + ".json"), bundle.getBytes(StandardCharsets.UTF_8));
                bien++;
            } catch (Throwable e) {
                StringWriter sw = new StringWriter();
                e.printStackTrace(new PrintWriter(sw));
                Files.write(salida.resolve(nombre + ".error"), sw.toString().getBytes(StandardCharsets.UTF_8));
                mal++;
            }
            System.out.println(nombre + " " + (System.nanoTime() - t0) / 1000000 + " ms");
        }
        System.out.println("hechos: " + bien + " bundle, " + mal + " error");
    }
}
