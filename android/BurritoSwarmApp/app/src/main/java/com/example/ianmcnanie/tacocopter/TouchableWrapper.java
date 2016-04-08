package com.example.ianmcnanie.tacocopter;

/**
 * Created by ianmcnanie on 3/22/16.
 */
import android.content.Context;
import android.view.MotionEvent;
import android.widget.FrameLayout;

public class TouchableWrapper extends FrameLayout {

    public TouchableWrapper(Context context) {
        super(context);
    }

    @Override
    public boolean dispatchTouchEvent(MotionEvent event) {

        switch (event.getAction()) {

            case MotionEvent.ACTION_DOWN:
                MapsActivity.mMapIsTouched = true;
                break;

            case MotionEvent.ACTION_UP:
                MapsActivity.mMapIsTouched = false;
                break;
        }
        return super.dispatchTouchEvent(event);
    }
}
