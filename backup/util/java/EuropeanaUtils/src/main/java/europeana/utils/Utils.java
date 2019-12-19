package europeana.utils;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.nio.file.Path;
import java.util.Properties;

import org.apache.log4j.Level;

public class Utils {
	
	public static Properties readProperties(InputStream is) throws IOException{
		Properties p = new Properties();
		p.load(is);
		return p;
	}
	
	public static Double scale(Double value, Double current_min, Double current_max, Double target_min, Double target_max) {
		return ((value - current_min) / (current_max - current_min)) * (target_max - target_min) + target_min;
	}
	
	public static void serialize(Object o, String serialization_file) throws IOException {
		FileOutputStream fileOut =  new FileOutputStream(serialization_file);
		ObjectOutputStream out = new ObjectOutputStream(fileOut);
        out.writeObject(o);
        out.close();
        fileOut.close();
	}
	
	
	public static Object deserialize(String serialization_file) throws IOException, ClassNotFoundException {
	    FileInputStream fileIn = new FileInputStream(serialization_file);
	    ObjectInputStream in = new ObjectInputStream(fileIn);
	    Object o = in.readObject();
	    in.close();
	    fileIn.close();
	    return o;
	}

}
