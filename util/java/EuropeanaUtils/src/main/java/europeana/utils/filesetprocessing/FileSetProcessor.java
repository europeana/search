package europeana.utils.filesetprocessing;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Enumeration;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.zip.ZipEntry;
import java.util.zip.ZipException;
import java.util.zip.ZipFile;

import org.apache.log4j.Logger;

import com.google.common.io.Files;

import europeana.utils.exception.ExceptionThreadFactory;

public class FileSetProcessor<T> {
	static Logger logger = Logger.getLogger(FileSetProcessor.class);
	
	ExceptionThreadFactory threadFactory;
	ExecutorService pool;
	Buffer<T> buffer;
	FileProcessor<T> fileProcessor;
	Integer nFiles = 0;

	public static Logger getLogger() {
		return logger;
	}

	public ExceptionThreadFactory getThreadFactory() {
		return threadFactory;
	}

	public ExecutorService getPool() {
		return pool;
	}

	public FileProcessor<T> getFileProcessor() {
		return fileProcessor;
	}

	public Buffer<T> getBuffer() {
		return buffer;
	}
	
	public FileSetProcessor(Integer buffersize, Integer numberThreads, FileProcessor<T> fileProcessor) {
		this.threadFactory = new ExceptionThreadFactory();
		this.pool = Executors.newFixedThreadPool(numberThreads, threadFactory);
		this.buffer = new Buffer<T>(buffersize);
		this.fileProcessor = fileProcessor;
	}
	
	public void start(File set) throws InterruptedException {
		nFiles = 0;
		ProcessSet(set);
		logger.info("Files sent to process: " + nFiles);
		pool.shutdown();
		pool.awaitTermination(Integer.MAX_VALUE, TimeUnit.DAYS);
		if (!buffer.isEmpty()) {
			fileProcessor.processBatchResults(buffer.retrieve());
		}
	}
	
	private void ProcessSet(File set) {
		if (set.isDirectory()) {
			ProcessFolder(set);
		} else if (Files.getFileExtension(set.getName()).equals("zip")) {
			ProcessZip(set);
		} else {
			ProcessFile(set);
		}
	}
	
	private void ProcessFolder(File folder) {
		File[] files = folder.listFiles();
		for (File file : files) {
			ProcessSet(file); 
		}
	}
	
	private void ProcessFile(File file) {
		try {
			InputStream stream = new FileInputStream(file);
			pool.execute(new RunnableFileProcessor<T>(fileProcessor, file.getName(), stream, buffer));
			nFiles++;
		} catch (IOException e) {
			logger.error("IO error: "+ file.getName());
			e.printStackTrace();
		}
	}
	
	private void ProcessZip(File zip) {
		try {
			ZipFile zipFile = new ZipFile(zip);
			Enumeration<? extends ZipEntry> entries = zipFile.entries();
			while(entries.hasMoreElements()){
				ZipEntry entry = entries.nextElement();
				if (entry.isDirectory()) {
				} else {
					threadFactory.setName(zip.getName() + "." + entry.getName());		
					InputStream stream = zipFile.getInputStream(entry);
					pool.execute(new RunnableFileProcessor<T>(fileProcessor, entry.getName(), stream, buffer));
					nFiles++;
				}
			}
			//zipFile.close();
		} catch (ZipException e) {
			logger.error("Zip file error: "+zip.getName());
			e.printStackTrace();
		} catch (IOException e) {
			logger.error("IO error: "+zip.getName());
			e.printStackTrace();
		}
	}
	
}
