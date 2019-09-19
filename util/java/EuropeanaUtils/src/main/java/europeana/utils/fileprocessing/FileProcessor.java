package europeana.utils.fileprocessing;

import java.io.InputStream;
import java.util.Collection;

public interface FileProcessor<T> {
	
	public T processFile(String id, InputStream stream);
	
	public void processBatchResults(Collection<T> results);
}
