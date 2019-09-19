package europeana.utils.fileprocessing;

import java.io.InputStream;

public class RunnableFileProcessor<T> implements Runnable {
	FileProcessor<T> processor;
	
	String id;
	InputStream stream;
	Buffer<T> buffer;
	
	public String getID() {
		return id;
	}
	
	public InputStream getStream() {
		return stream;
	}
	
	public Buffer<T> getBuffer(){
		return buffer;
	}
	
	public RunnableFileProcessor(FileProcessor<T> processor, String id, InputStream stream, Buffer<T> buffer) {
		this.processor = processor;
		this.id = id;
		this.stream = stream;
		this.buffer = buffer;
	}

	
	@Override
	public void run() {
		T result = processor.processFile(id,stream);
		if (result != null) {
			if (buffer.isFull()) {
				processor.processBatchResults(buffer.retrieve());
			}
			buffer.add(result);
		}
		
	}
}
