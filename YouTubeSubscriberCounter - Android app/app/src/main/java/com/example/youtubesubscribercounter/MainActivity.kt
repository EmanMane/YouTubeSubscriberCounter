package com.example.youtubesubscribercounter

import android.content.Intent
import android.content.res.Configuration
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.EditText
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.eclipse.paho.client.mqttv3.*
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence
import retrofit2.Call
import retrofit2.Response

class MainActivity : AppCompatActivity() {

    // Declaration of the layout elements
    private lateinit var channelsRecycler: RecyclerView
    private lateinit var adapter: ChannelAdapter
    private lateinit var addButton: Button
    private lateinit var removeAllButton: Button
    private lateinit var inputText: EditText

    // IMPORTANT! Use your own key because every key has daily limit of calls (Sikiric, Kapic)
    private val apiKey = "ENTER KEY HERE"

    // Declaration of the MQTT client
    private val brokerUrl = "tcp://broker.hivemq.com:1883"
    private val clientId = "kotlin_client_UsProject" // Needs to be unique
    private lateinit var mqttClient: MqttClient

    // MQTT Themes
    private val addTheme = "UsProject/channel/add"
    private val removeTheme = "UsProject/channel/remove"
    private val removeAllTheme = "UsProject/channel/removeAll"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Disable dark mode for better UI experience
        if (isDarkModeEnabled()) {
            setLightMode()
        }

        setContentView(R.layout.activity_main)

        // MQTT connection
        connect()

        channelsRecycler = findViewById(R.id.channel_recycler)
        // Initialization of the ChannelAdapter with the callback function
        // Function is the one that is being called when item of recycler is removed (when trash can image is pressed)
        // Adapter is empty everytime the app starts!
        adapter = ChannelAdapter(mutableListOf()) { channel ->
            publishRemoveChannel(channel)
        }

        // Initialization of View elements
        addButton = findViewById(R.id.add_button)
        removeAllButton = findViewById(R.id.remove_all_button)
        inputText = findViewById(R.id.channel_input)

        // If channel url is shared from YouTube application
        if (intent?.action == Intent.ACTION_SEND && intent?.type == "text/plain") {
            handleSendText(intent)
        }

        // Initialization of RecyclerView
        channelsRecycler.adapter = adapter
        channelsRecycler.layoutManager = LinearLayoutManager(this)

        // Setup of onclick listeners for Remove All button and Add button
        addButton.setOnClickListener {
            if(inputText.text.toString().contains("https://youtube.com/@")){
                val url = inputText.text.toString().trim()
                val pattern = Regex("""/@(.+)$""")
                val matchResult = pattern.find(url)
                val handle = matchResult?.groupValues?.get(1)
                if (handle != null && handle.isNotBlank()) {
                    onClickAdd(handle)
                    inputText.text.clear()
                }
            }else{
                onClickAdd(inputText.text.toString())
                inputText.text.clear()
            }

        }

        removeAllButton.setOnClickListener {
            adapter.removeAllItems()
            publishRemoveAll()
        }
    }


    /**
     * Checks if the device has dark mode set
     */
    private fun isDarkModeEnabled(): Boolean {
        return when (resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK) {
            Configuration.UI_MODE_NIGHT_YES -> true
            else -> false
        }
    }

    /**
     * Sets UI to light mode
     */
    private fun setLightMode() {
        delegate.localNightMode = AppCompatDelegate.MODE_NIGHT_NO
    }

    /**
     * Sets Intent text into EditText
     */
    private fun handleSendText(intent: Intent) {
        intent.getStringExtra(Intent.EXTRA_TEXT)?.let {
            inputText.setText(it)
        }
    }

    /**
     * Handles text intent from anywhere inside the android device
     */
    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        if (intent?.action == Intent.ACTION_SEND && intent?.type == "text/plain") {
            handleSendText(intent)
        }
    }

    /**
     * Function that is called each time Add button is pressed
     *
     * It handles the fetching of data from YouTube API (using coroutines) based on the provided parameter.
     * It also calls the proper functions to change the recycler elements (addition of a new element)
     */
    private fun onClickAdd(parameter: String) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val channel = fetchChannel(parameter)
                if (channel != null) {
                    val channelWithDetails = fetchChannelDetails(channel)
                    if (channelWithDetails != null) {
                        publishChannel(channelWithDetails)

                        // Important! Must switch to Main because of the adapter change
                        withContext(Dispatchers.Main) {
                            adapter.addItem(channelWithDetails)
                            inputText.text.clear()
                        }
                    } else {
                        // Handling of failure to fetch channel details (no current need for this)
                    }
                } else {
                    // Handle failure to fetch channel (no current need for this)
                }

            } catch (e: Exception) {
                // Handle any exceptions that occur during the network call (no current need for this)
                e.printStackTrace()
            }
        }
    }

    /**
     * This function uses YouTube API (/search endpoint) which returns one (set in maxResults) channel (set in type)
     * based on the parameter string that this function accepts.
     *
     * It is worth noting that the "part" is set to "snippet" and it doesn't return any channel statistics such as subscriber or view count (unsupported on search endpoint).
     * That is why we need to use another endpoint (/channel) which allows statistics in "part" and returns sub and view count.
     *
     * @return Search object compatible with /search endpoint call result
     */
    private fun fetchChannel(parameter: String): Search? {
        // Needed parameter declaration
        val part = "snippet"
        val maxResults = 1
        val type = "channel"

        // Call setup, execution and return
        val call: Call<SearchResponse>? =
            YouTubeApiConfig.retrofit.getChannelsByHandle(part, maxResults, type, parameter, apiKey)
        val response: Response<SearchResponse>? = call?.execute()
        return if (response != null && response.isSuccessful) {
            val searchResponse = response.body() // list of Search objects
            searchResponse?.items?.get(0) // we always fetch first because the maxResults is set to 1 result
        } else {
            // Handling of the unsuccessful response or exception (no current need for this)
            null
        }
    }

    /**
     * Connects to (/channel) endpoint and gets the statistics data based on the channelID
     *
     * This function basically converts Search object to Channel object
     */
    private fun fetchChannelDetails(channel: Search): Channel? {
        val part = "snippet,statistics"

        val channelId = channel.id?.channelID

        val call: Call<ChannelResponse>? =
            channelId?.let { YouTubeApiConfig.retrofit.getChannelDetails(part, it, apiKey) }

        return try {
            val response: Response<ChannelResponse>? = call?.execute()
            if (response != null && response.isSuccessful) {
                val searchResponse = response.body()
                searchResponse?.items?.get(0)
            } else {
                null
            }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    /**
     * Publishes a channel in JSON format to a theme defined for adding new channels
     */
    private fun publishChannel(channel: Channel) {
        val name = channel.snippet?.title
        val viewCount = channel.statistics?.viewCount
        val subscriberCount = channel.statistics?.subscriberCount
        val jsonPayload = "{\"name\": \"$name\", \"viewCount\": $viewCount, \"subscriberCount\": $subscriberCount}"
        val mqttMessage = MqttMessage(jsonPayload.toByteArray())
        mqttClient.publish(addTheme, mqttMessage)
    }

    /**
     * Publishes a channel in JSON format to a theme defined for removing the provided channel
     */
    fun publishRemoveChannel(channel: Channel) {
        val name = channel.snippet?.title
        val viewCount = channel.statistics?.viewCount
        val subscriberCount = channel.statistics?.subscriberCount
        val jsonPayload = "{\"name\": \"$name\", \"viewCount\": $viewCount, \"subscriberCount\": $subscriberCount}"
        val mqttMessage = MqttMessage(jsonPayload.toByteArray())
        mqttClient.publish(removeTheme, mqttMessage)
    }

    /**
     * Publishes a string in JSON format to a theme defined for removing every currently active channel
     */
    private fun publishRemoveAll() {
        val jsonPayload = "{\"removeAll\": \"true\"}"  // Used only so that something is sent
        val mqttMessage = MqttMessage(jsonPayload.toByteArray())
        mqttClient.publish(removeAllTheme, mqttMessage)
    }

    /**
     * Override to disconnect from MQTT (just in case :))
     */
    override fun onDestroy() {
        super.onDestroy()
        mqttClient.disconnect()
    }

    /**
     * Connects to MQTT server and subscribes to predefined themes
     */
    private fun connect() {
        try {
            // Configuration of connection
            mqttClient = MqttClient(brokerUrl, clientId, MemoryPersistence())
            val options = MqttConnectOptions()
            options.isCleanSession = true
            mqttClient.connect(options)
            println("Connected to MQTT broker")

            // Subscribe to topics
            mqttClient.subscribe(addTheme)
            mqttClient.subscribe(removeAllTheme)
            mqttClient.subscribe(removeTheme)

            // Set callback for message arrival
            mqttClient.setCallback(object : MqttCallback {
                override fun connectionLost(cause: Throwable?) {
                    println("Connection lost: ${cause?.message}")
                }

                override fun messageArrived(topic: String?, message: MqttMessage?) {
                    println("Message arrived on topic: $topic")
                    println("Payload: ${message?.payload?.let { String(it) }}")
                }

                override fun deliveryComplete(token: IMqttDeliveryToken?) {
                    println("Message delivered")
                }
            })
        } catch (e: MqttException) {
            println("Error connecting to MQTT broker: ${e.message}")
        }
    }
}
