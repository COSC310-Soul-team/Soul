package soul;
import java.io.*;
import java.net.*;
import java.util.*;

import javax.naming.spi.DirStateFactory.Result;

public class SoulServer {
	private int welcomePort = 1234;
	private ArrayList<Integer[]> questionAnswers = new ArrayList<Integer[]>();
	//user file format: userId.txt->password, name, rule, courses
	//request format: reg/log + name + userId + password
	public static void main(String[] args) {
		
		
	}
	//each new connection is a new thread?
	//each connection does one thing
	public void commandProcessor() {
		try {
			ServerSocket welcomeSocket = new ServerSocket(welcomePort);

//				Socket socket = welcomeSocket.accept();
				InputStream input = socket.getInputStream();
	            BufferedReader clientReader = new BufferedReader(new InputStreamReader(input));
	            String request = clientReader.readLine();//need to terminate by \n!!!
	            StringTokenizer tokens = new StringTokenizer(request);
	            String command = tokens.nextToken();
	            if (command.equals("reg")) { //registration
					String regUserId = tokens.nextToken();
					String regPassword = tokens.nextToken();
					String regName = tokens.nextToken();
	            	String regRule = tokens.nextToken();
					File regUser = new File(regUserId+".txt");
					BufferedWriter bw = new BufferedWriter(new FileWriter(regUser));
					bw.write(regUserId+" "+regName+" "+regPassword+" "+regRule);
				} else if(command.equals("log")){ //login, change status
					 String userId = tokens.nextToken(); //first line from client must be userId
			         String password = tokens.nextToken();//second line must be password
			         try {
				            FileReader fReader = new FileReader(userId+".txt");
				            BufferedReader bReader = new BufferedReader(fReader);
				            if (password.equals(bReader.readLine())) {
								if (bReader.readLine().equals("s")) {
									new StudentProcessor(socket, this).start();
								} else {
									new teacherProcessor(socket).start();
								}
							} else {
								socket.close();
							}
						} catch (FileNotFoundException e) {
							socket.close();
						}
				}	           	            
		} catch (Exception e) {
			e.printStackTrace();
		}
		
	}
}

class requestHandler extends Thread{
	//reg(register), log(login), send(teacher send pictures), 
	//sadd(student add course), tadd(teacher add course), del?
	//start/stop? senta(teacher send answer)?
	//every time teacher send picture, increment question number
	//verify rules?
	//student change answer?
	private Socket socket;
	private InputStream is = null;
	private DataOutputStream os = null;
	private BufferedReader br = null;
	private BufferedWriter bw = null;
	
	public requestHandler(Socket socket) {
		this.socket = socket;
	}
	@Override
	public void run() {
		try {
//				Socket socket = welcomeSocket.accept();
				InputStream is = socket.getInputStream();
	            br = new BufferedReader(new InputStreamReader(is));
	            String request = br.readLine();//need to terminate by \n!!!
	            StringTokenizer tokens = new StringTokenizer(request);
	            String command = tokens.nextToken();
	            os = new DataOutputStream(socket.getOutputStream());
	            if (command.equals("reg")) { //registration
					String regUserId = tokens.nextToken();
					String regPassword = tokens.nextToken();
					String regName = tokens.nextToken();
	            	String regRule = tokens.nextToken();
					File regUser = new File(regUserId+".txt");
					bw = new BufferedWriter(new FileWriter(regUser));
					bw.write(regUserId+" "+regName+" "+regPassword+" "+regRule);
					os.writeBytes("registered");
				} else if(command.equals("log")){ //login, change status
					 String userId = tokens.nextToken(); //first line from client must be userId
			         String password = tokens.nextToken();//second line must be password
			         try {
				            FileReader fReader = new FileReader(userId+".txt");
				            br = new BufferedReader(fReader);
				            tokens = new StringTokenizer(br.readLine());
				            tokens.nextToken();
				            if (tokens.nextToken().equals(password)) {
				            	os.writeBytes("validUser");
							} else {
								os.writeBytes("invalidUser");
								socket.close();
							}
						} catch (FileNotFoundException e) {
							os.writeBytes("userNotFound");
							socket.close();
						}
				}	           	            
		} catch (Exception e) {
			e.printStackTrace();
		}		
	}
	private void sendResponse(String st)
    {	// Sends one line response and closes socket and input/output buffers
    	try {
    		os.writeBytes(st);
    	}
    	catch (Exception e)
    	{
    		System.out.println(e);
    	}
    	finally
    	{	try
    		{ br.close(); }
    		catch (Exception e) { System.out.println(e); }
    		try
    		{ os.close(); }
    		catch (Exception e) { System.out.println(e); }
    		try
    		{ socket.close(); }
    		catch (Exception e) { System.out.println(e); }
    	}
    }
}

class StudentProcessor extends Thread{
//	send characters and receive pictures, output is pic, input is text
	private Socket studentSocket;
	private SoulServer server;
	public StudentProcessor(Socket socket, SoulServer s) {
		this.studentSocket = socket;
		server = s;
	}
	public void run() {
		try {
			InputStream input = studentSocket.getInputStream();
            BufferedReader reader = new BufferedReader(new InputStreamReader(input));	
            String inputString = reader.readLine();
			while (inputString!=null) {
				System.out.println(inputString);
				inputString = reader.readLine();
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	
	}
}
class teacherProcessor extends Thread{
//	send pictures and receive characters, output is text(or int), input is pic
	private Socket teacherSocket;
	public teacherProcessor(Socket socket) {
		this.teacherSocket = socket;
	}
	public void run() {
		try {
			OutputStream output = teacherSocket.getOutputStream();
            PrintWriter writer = new PrintWriter(output, true);	
            
		} catch (Exception e) {
			e.printStackTrace();
		}
		
	}
}

//class UDPProcessor implements Runnable{
//private static int UDPPort = 1235;
//private SoulServer server;
//
//public UDPProcessor(SoulServer s)
//{
//	server = s;
//}
//
//public void run{
//	DatagramSocket serverSocket = new DatagramSocket();
//	byte[] receiveData = new byte[1024];
//	try {
//		while (true) {
//			DatagramPacket receivePacket = new DatagramPacket(receiveData, receiveData.length);
//			serverSocket.receive(receivePacket);
//		}
//	} catch (Exception e) {
//		// TODO: handle exception
//		System.out.println(e);
//	}
//}
//}






