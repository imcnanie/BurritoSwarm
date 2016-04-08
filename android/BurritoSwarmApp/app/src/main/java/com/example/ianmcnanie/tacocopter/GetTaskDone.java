package com.example.ianmcnanie.tacocopter;

import android.content.Context;
import android.os.AsyncTask;
import android.widget.Toast;

import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;


/**
 * Created by ianmcnanie on 3/22/16.
 */



class GetTaskDone extends AsyncTask<MyTaskParams, Void, String> {

    /*@Override
    protected void onPreExecute() {
        super.onPreExecute();
        Toast.makeText(getApplicationContext(), "this is my toast",
                Toast.LENGTH_LONG).show();
    }*/

    protected String doInBackground(MyTaskParams... params) {

        HttpResponse response = null;
        try {
            HttpClient client = new DefaultHttpClient();
            HttpGet request = new HttpGet();


            //fly_here.setText("Fly Here: " + separated[1].trim());

            request.setURI(new URI("http://10.1.1.120:8080/deliver/"+params[0].gps_coords));
            response = client.execute(request);
        } catch (URISyntaxException e) {
            e.printStackTrace();
        } catch (ClientProtocolException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        return null;
    }

    /*@Override
    protected void onPostExecute(String result) {
        super.onPostExecute(result);
        Toast.makeText(MapsActivity.getApplicationContext(), result,
                Toast.LENGTH_LONG).show();
    }*/
}
