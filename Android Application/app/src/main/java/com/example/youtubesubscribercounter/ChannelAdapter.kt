package com.example.youtubesubscribercounter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.squareup.picasso.Picasso
import jp.wasabeef.picasso.transformations.RoundedCornersTransformation
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.eclipse.paho.client.mqttv3.MqttException

class ChannelAdapter(private val itemList: MutableList<Channel>,
                     private val publishRemoveCallback: (Channel) -> Unit) :
    RecyclerView.Adapter<ChannelAdapter.ViewHolder>() {

    // ViewHolder class for item views
    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val channelName: TextView = view.findViewById(R.id.item_name)
        val channelImage: ImageView = view.findViewById(R.id.channel_profile)
        val removeButton: ImageButton = view.findViewById(R.id.remove_item)
    }

    // Create new views (invoked by the layout manager)
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_cardview, parent, false)
        return ViewHolder(view)
    }

    // Replace the contents of a view (invoked by the layout manager)
    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val channel = itemList[position]

        // Set the text and click listener for the TextView
        holder.channelName.text = channel.snippet?.title

        // Load the image using the URL from the channel object
        val imageUrl = channel.snippet?.thumbnails?.default?.url
        if (!imageUrl.isNullOrEmpty()) {
            Picasso.get()
                .load(imageUrl)
                .transform(RoundedCornersTransformation(16, 0))
                .into(holder.channelImage)
        }

        // Set the click listener for the ImageButton
        holder.removeButton.setOnClickListener {
            val currentPosition = holder.adapterPosition
            if (currentPosition != RecyclerView.NO_POSITION) {
                // Remove the item from the dataset
                itemList.removeAt(currentPosition)

                // Notify the adapter about the item removal
                notifyItemRemoved(currentPosition)
            }
            publishRemoveCallback(channel)
        }

    }

    // Return the size of the dataset (invoked by the layout manager)
    override fun getItemCount(): Int {
        return itemList.size
    }

    // Add a new item to the dataset
    fun addItem(item: Channel) {
        itemList.add(item)
        notifyItemInserted(itemList.size - 1)
    }

    // Function to remove all items from the RecyclerView
    suspend fun removeAllItems() {
        withContext(Dispatchers.Main){
            for (i in itemList.size - 1 downTo  0){
                itemList.removeAt(i)
                try{
                    notifyItemRemoved(i)
                }
                catch(error : Exception){
                    println(error.message)
                    println(error.stackTrace)
                }

            }
        }

    }

    fun getChannels() : MutableList<Channel>{
         return itemList
    }

    suspend fun removeAtIndex(index : Int){
        withContext(Dispatchers.Main){
            itemList.removeAt(index)
            notifyDataSetChanged()
        }

    }
}
