package @PACKAGE_PATH@.data

import android.content.Context
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore(name = "settings")

class SettingsRepo(private val context: Context) {
    private val KEY_DARK = booleanPreferencesKey("dark_override")
    private val KEY_USER_NAME = stringPreferencesKey("user_name")

    val darkOverride: Flow<Boolean?> = context.dataStore.data.map { it[KEY_DARK] }
    val userName: Flow<String> = context.dataStore.data.map { it[KEY_USER_NAME].orEmpty() }

    suspend fun setDarkOverride(value: Boolean?) {
        context.dataStore.edit { prefs ->
            if (value == null) prefs.remove(KEY_DARK) else prefs[KEY_DARK] = value
        }
    }

    suspend fun setUserName(name: String) {
        context.dataStore.edit { prefs -> prefs[KEY_USER_NAME] = name }
    }
}
