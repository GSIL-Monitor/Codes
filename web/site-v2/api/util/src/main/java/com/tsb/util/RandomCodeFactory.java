package com.tsb.util;
import java.util.Random;

/**
 * *
 * @author Arthur
 *
 */
public class RandomCodeFactory {

	private static Random random = new Random(System.currentTimeMillis());
	private static char[] ca = new char[]{'0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'};

	/**
	 *
	 * @param n
	 * @return
	 */
	public static synchronized String generate(int n){
		char[] cr = new char[n];
		for (int i=0;i<n;i++) {
			int x = random.nextInt(10);
			cr[i] = Integer.toString(x).charAt(0);
		}
		return (new String(cr));
	}

	public static synchronized String generateMixed(int n){
		char[] cr = new char[n];
		for (int i=0;i<n;i++){
			int x = random.nextInt(36);
			cr[i] = ca[x];
		}
		return (new String(cr));
	}

	public static synchronized int nextInt(int n){
		return random.nextInt(n);
	}

}
