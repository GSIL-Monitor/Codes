package com.tsb.company.util;

import org.springframework.stereotype.Component;

@Component
public class CommonParseUtil {

	public static String parseDesc(String desc) {
		if (null!=desc&&desc != "") {
			if (desc.length() > 80)
				desc = desc.substring(0, 80) + "...";
		}

		return desc;
	}

	// 只显示5个tag
	public static String parseTags(String tags) {
		String tagResult = "";
		if (null != tags&&tags!="") {
			String regex = ",|，|\\s+";
			String[] tagList = tags.split(regex);
			int size = 0;
			size = tagList.length > 5 ? 5 : tagList.length;
			for (int i = 0; i < size; i++) {
				tagResult += tagList[i]+" ";
			}
			tagResult = tagResult.substring(0, tagResult.length() - 1);
		}
		

		return tagResult;
	}

}
