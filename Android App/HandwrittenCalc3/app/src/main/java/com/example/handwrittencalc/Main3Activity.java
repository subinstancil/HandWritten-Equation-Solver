package com.example.handwrittencalc;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;



public class Main3Activity extends AppCompatActivity {
    String selectedImagePath;
    Button b;
    TextView t;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main3);
        b=findViewById(R.id.btn);
        t=findViewById(R.id.responseText);
        Intent i =getIntent();
       t.setText(i.getStringExtra("response"));
        b.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent i = new Intent(getApplicationContext(),Main4Activity.class);
                startActivity(i);
            }
        });


    }

}