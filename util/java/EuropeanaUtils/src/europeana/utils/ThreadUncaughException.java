package europeana.utils;

import java.lang.Thread.UncaughtExceptionHandler;

import org.apache.log4j.Logger;

public class ThreadUncaughException implements UncaughtExceptionHandler {
	static Logger logger = Logger.getLogger(ThreadUncaughException.class);
	
	@Override
	public void uncaughtException(Thread t, Throwable e) {
		logger.error("Thread Exception at thread "+ t.getName() + " - Message: " + e.getMessage());
		e.printStackTrace();
	}

}
