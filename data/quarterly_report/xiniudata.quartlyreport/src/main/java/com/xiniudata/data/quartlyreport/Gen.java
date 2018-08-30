package com.xiniudata.data.quartlyreport;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.apache.poi.xwpf.usermodel.XWPFRun;
import org.apache.poi.xwpf.usermodel.XWPFTable;
import org.apache.poi.xwpf.usermodel.XWPFTableCell;
import org.apache.poi.xwpf.usermodel.XWPFTableRow;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTTc;

/**
 * Hello world!
 *
 */
public class Gen {
	/**
	 * 用一个docx文档作为模板，然后替换其中的内容，再写入目标文档中。
	 * 
	 * @throws Exception
	 */
	public void gen() throws Exception {
		Map<String, Object> params = new HashMap<String, Object>();
		params.put("title", "测试报告");
		
		String filePath = "samples/QReport.docx";
		InputStream is = new FileInputStream(filePath);
		XWPFDocument doc = new XWPFDocument(is);
		// 替换段落里面的变量
		this.replaceInPara(doc, params);
		// 替换表格里面的变量
		this.replaceInTable(doc, params);
		OutputStream os = new FileOutputStream("result/test.docx");
		doc.write(os);
		this.close(os);
		this.close(is);
	}

	/**
	 * 替换段落里面的变量
	 * 
	 * @param doc
	 *            要替换的文档
	 * @param params
	 *            参数
	 */
	private void replaceInPara(XWPFDocument doc, Map<String, Object> params) {
		Iterator<XWPFParagraph> iterator = doc.getParagraphsIterator();
		XWPFParagraph para;
		while (iterator.hasNext()) {
			para = iterator.next();
			this.replaceInPara(para, params);
		}
	}

	/**
	 * 替换段落里面的变量
	 * 
	 * @param para
	 *            要替换的段落
	 * @param params
	 *            参数
	 */
	private void replaceInPara(XWPFParagraph para, Map<String, Object> params) {
		List<XWPFRun> runs;
		Matcher matcher;
		if (this.matcher(para.getParagraphText()).find()) {
			runs = para.getRuns();
			for (int i = 0; i < runs.size(); i++) {
				XWPFRun run = runs.get(i);
				String runText = run.toString();
				matcher = this.matcher(runText);
				if (matcher.find()) {
					while ((matcher = this.matcher(runText)).find()) {
						runText = matcher.replaceFirst(String.valueOf(params.get(matcher.group(1))));
					}
					// 直接调用XWPFRun的setText()方法设置文本时，在底层会重新创建一个XWPFRun，把文本附加在当前文本后面，
					// 所以我们不能直接设值，需要先删除当前run,然后再自己手动插入一个新的run。
					//para.removeRun(i);
					//para.insertNewRun(i).setText(runText);
					run.setText(runText, 0);
				}
			}
		}
	}

	/**
	 * 替换表格里面的变量
	 * 
	 * @param doc
	 *            要替换的文档
	 * @param params
	 *            参数
	 */
	private void replaceInTable(XWPFDocument doc, Map<String, Object> params) {
		Iterator<XWPFTable> iterator = doc.getTablesIterator();
		XWPFTable table;
		List<XWPFTableRow> rows;
		List<XWPFTableCell> cells;
		List<XWPFParagraph> paras;
		while (iterator.hasNext()) {
			table = iterator.next();
			//table.addRow(table.getRow(1));
			//table.removeRow(1);
			rows = table.getRows();
			for (XWPFTableRow row : rows) {
				cells = row.getTableCells();
				//CTTc cttc = cells.get(0).getCTTc();
				//XWPFTableCell new_cell = row.addNewTableCell();
				//new_cell.getCTTc().setTcPr(cttc.getTcPr());
				//new_cell.getCTTc().setPArray(cttc.getPArray());
				
				for (XWPFTableCell cell : cells) {
					paras = cell.getParagraphs();
					for (XWPFParagraph para : paras) {
						this.replaceInPara(para, params);
					}
				}
			}
		}
	}
	
	private XWPFTable findTable(XWPFDocument doc, String name) {
		Iterator<XWPFTable> iterator = doc.getTablesIterator();
		XWPFTable table;
		List<XWPFTableRow> rows;
		List<XWPFTableCell> cells;
		List<XWPFParagraph> paras;
		while (iterator.hasNext()) {
			table = iterator.next();
			rows = table.getRows();
			for (XWPFTableRow row : rows) {
				cells = row.getTableCells();
				for (XWPFTableCell cell : cells) {
					paras = cell.getParagraphs();
					for (XWPFParagraph para : paras) {
						List<XWPFRun> runs;
						Matcher matcher;
						if (this.matcher(para.getParagraphText()).find()) {
							runs = para.getRuns();
							for (int i = 0; i < runs.size(); i++) {
								XWPFRun run = runs.get(i);
								String runText = run.toString();
								matcher = this.matcher(runText);
								if (matcher.find()) {
									while ((matcher = this.matcher(runText)).find()) {
										runText = matcher.replaceFirst(String.valueOf(params.get(matcher.group(1))));
									}
									// 直接调用XWPFRun的setText()方法设置文本时，在底层会重新创建一个XWPFRun，把文本附加在当前文本后面，
									// 所以我们不能直接设值，需要先删除当前run,然后再自己手动插入一个新的run。
									//para.removeRun(i);
									//para.insertNewRun(i).setText(runText);
									run.setText(runText, 0);
								}
							}
						}
					}
				}
			}
		}
	}

	/**
	 * 正则匹配字符串
	 * 
	 * @param str
	 * @return
	 */
	private Matcher matcher(String str) {
		Pattern pattern = Pattern.compile("\\$\\{(.+?)\\}", Pattern.CASE_INSENSITIVE);
		Matcher matcher = pattern.matcher(str);
		return matcher;
	}

	/**
	 * 关闭输入流
	 * 
	 * @param is
	 */
	private void close(InputStream is) {
		if (is != null) {
			try {
				is.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}

	/**
	 * 关闭输出流
	 * 
	 * @param os
	 */
	private void close(OutputStream os) {
		if (os != null) {
			try {
				os.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}

	public static void main(String[] args) throws Exception{
		Gen gen = new Gen();
		gen.gen();
		System.out.print("End.");
	}
}
