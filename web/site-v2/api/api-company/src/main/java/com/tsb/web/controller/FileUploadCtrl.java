package com.tsb.web.controller;

import java.io.File;
import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.multipart.MultipartFile;

import com.mongodb.DB;
import com.mongodb.MongoClient;
import com.mongodb.gridfs.GridFS;
import com.mongodb.gridfs.GridFSInputFile;
import com.tsb.vo.MongodbConstant;

@Controller
@RequestMapping(value = "/api/company/file")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class FileUploadCtrl extends BaseController {
	@Autowired
	private MongodbConstant mongodbConstant;
	
	@RequestMapping(value = "upload", method=RequestMethod.POST)
	@ResponseBody
	public Object upload(@RequestParam(value = "file", required = false) MultipartFile file) {
		String fileName = file.getOriginalFilename(); 
		//System.out.println(fileName);
		//System.out.println(mongodbConstant.getHost());
        //System.out.println(file.getContentType());
        
		Map map = new HashMap();
		map.put("code", 0);
		
		File targetFile = new File(mongodbConstant.getFileDir(), fileName); 
		try {  
            file.transferTo(targetFile);  
        } catch (Exception e) {  
            e.printStackTrace();  
        }  
		
        MongoClient mongoClient = new MongoClient( mongodbConstant.getHost() );
        try{
        	DB db = new DB(mongoClient, "gridfs");
            GridFS myFS = new GridFS(db);
            GridFSInputFile gfile = myFS.createFile(targetFile);  
	        gfile.setContentType(file.getContentType());
	        gfile.save();  
	        map.put("fileName", fileName);
	        map.put("gridId", gfile.getId().toString());
        }
        catch(Exception e){
        	e.printStackTrace();
        }
        finally{
        	mongoClient.close();
        }
        
        targetFile.delete();

		return map;
	}
	
	public static void main(String[] args) {
		
	}
}
