package europeana.utils.exception;

import java.util.concurrent.Executors;
import java.util.concurrent.ThreadFactory;

public class ExceptionThreadFactory implements ThreadFactory {
	
	private String threadName = null;
	
	public void setName(String threadName) {
		this.threadName = threadName;
	}

	@Override
	public Thread newThread(Runnable r) {
	    Thread thread = Executors.defaultThreadFactory().newThread(r);
	    thread.setUncaughtExceptionHandler(new ThreadUncaughException());
	    if (threadName != null) {
	    	thread.setName(threadName);
	    }
	    return thread;
	}

}
